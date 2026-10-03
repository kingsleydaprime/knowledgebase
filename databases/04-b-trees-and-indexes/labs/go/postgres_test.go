package btree

// The same PostgreSQL checks through pgx. Run through ../shared/with-postgres.sh, which sets PGHOST etc.;
// without it, these tests skip.

import (
	"context"
	"os"
	"strings"
	"testing"

	"github.com/jackc/pgx/v5"
)

type planNode = map[string]any

func nodes(plan planNode) []planNode {
	out := []planNode{plan}
	children, _ := plan["Plans"].([]any)
	for _, c := range children {
		out = append(out, nodes(c.(planNode))...)
	}
	return out
}

func connect(t *testing.T) (*pgx.Conn, context.Context) {
	t.Helper()
	if os.Getenv("PGHOST") == "" {
		t.Skip("no PostgreSQL: run through ../shared/with-postgres.sh")
	}
	ctx := context.Background()
	conn, err := pgx.Connect(ctx, "") // an empty string: take everything from the PG* environment variables
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { conn.Close(ctx) })
	setup, err := os.ReadFile("../shared/orders.sql")
	if err != nil {
		t.Fatal(err)
	}
	for _, statement := range strings.Split(string(setup), ";\n") {
		if strings.TrimSpace(stripComments(statement)) != "" {
			if _, err := conn.Exec(ctx, statement); err != nil { // one at a time, as VACUUM requires
				t.Fatal(err)
			}
		}
	}
	return conn, ctx
}

func stripComments(sql string) string {
	var lines []string
	for _, line := range strings.Split(sql, "\n") {
		if !strings.HasPrefix(strings.TrimSpace(line), "--") {
			lines = append(lines, line)
		}
	}
	return strings.Join(lines, "\n")
}

func explain(t *testing.T, conn *pgx.Conn, ctx context.Context, sql string) []planNode {
	t.Helper()
	// EXPLAIN's JSON is a list holding one object: {"Plan": {…}, "Planning Time": 0.1, …}. Its values have
	// different types, so it decodes into map[string]any, and the plan is picked out with a type assertion.
	var plans []map[string]any
	if err := conn.QueryRow(ctx, "EXPLAIN (ANALYZE, BUFFERS, TIMING OFF, FORMAT JSON) "+sql).Scan(&plans); err != nil {
		t.Fatal(err)
	}
	return nodes(plans[0]["Plan"].(planNode))
}

func pages(plan []planNode) float64 {
	return plan[0]["Shared Hit Blocks"].(float64) + plan[0]["Shared Read Blocks"].(float64) // JSON numbers are float64
}

func TestPostgres(t *testing.T) {
	conn, ctx := connect(t) // one load of the million rows for all the checks below

	t.Run("three levels, and a lookup reads four pages", func(t *testing.T) {
		var level int64
		if err := conn.QueryRow(ctx, "SELECT level FROM bt_metap('orders_pkey')").Scan(&level); err != nil || level != 2 {
			t.Fatal(level, err)
		}
		if plan := explain(t, conn, ctx, "SELECT * FROM orders WHERE id = 424242"); plan[0]["Node Type"] != "Index Scan" || pages(plan) != 4 {
			t.Fatal(plan[0]["Node Type"], pages(plan))
		}
	})

	t.Run("a composite index serves its leading column, not the second alone", func(t *testing.T) {
		conn.Exec(ctx, "CREATE INDEX orders_customer_created ON orders (customer_id, created_at)")
		defer conn.Exec(ctx, "DROP INDEX orders_customer_created")
		used := false
		for _, n := range explain(t, conn, ctx, "SELECT * FROM orders WHERE customer_id = 42 AND created_at > '2026-06-01'") {
			used = used || n["Index Name"] == "orders_customer_created"
		}
		hour := explain(t, conn, ctx, "SELECT * FROM orders WHERE created_at >= '2026-06-01' AND created_at < '2026-06-01 01:00'")
		if !used || hour[0]["Node Type"] != "Seq Scan" {
			t.Fatal(used, hour[0]["Node Type"])
		}
	})

	t.Run("an index-only scan needs a vacuumed table", func(t *testing.T) {
		conn.Exec(ctx, "CREATE INDEX orders_customer_total ON orders (customer_id) INCLUDE (total)")
		defer conn.Exec(ctx, "DROP INDEX orders_customer_total")
		conn.Exec(ctx, "VACUUM orders")
		clean := explain(t, conn, ctx, "SELECT total FROM orders WHERE customer_id = 42")
		conn.Exec(ctx, "UPDATE orders SET total = total + 1 WHERE customer_id = 42")
		dirty := explain(t, conn, ctx, "SELECT total FROM orders WHERE customer_id = 42")
		if clean[0]["Node Type"] != "Index Only Scan" || clean[0]["Heap Fetches"] != 0.0 || dirty[0]["Heap Fetches"].(float64) == 0 {
			t.Fatal(clean[0]["Heap Fetches"], dirty[0]["Heap Fetches"])
		}
	})
}
