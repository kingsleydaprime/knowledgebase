package joins

// The PostgreSQL checks through pgx. Run through ../shared/with-postgres.sh; without it, these tests skip.

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

func TestPostgres(t *testing.T) {
	if os.Getenv("PGHOST") == "" {
		t.Skip("no PostgreSQL: run through ../shared/with-postgres.sh")
	}
	ctx := context.Background()
	db, err := pgx.Connect(ctx, "")
	if err != nil {
		t.Fatal(err)
	}
	defer db.Close(ctx)
	setup, _ := os.ReadFile("../shared/shop.sql")
	for _, statement := range strings.Split(string(setup), ";\n") {
		code := ""
		for _, line := range strings.Split(statement, "\n") {
			if !strings.HasPrefix(strings.TrimSpace(line), "--") {
				code += line
			}
		}
		if strings.TrimSpace(code) != "" {
			if _, err := db.Exec(ctx, statement); err != nil {
				t.Fatal(err)
			}
		}
	}
	explain := func(sql string) []planNode {
		var plans []map[string]any
		if err := db.QueryRow(ctx, "EXPLAIN (ANALYZE, BUFFERS, TIMING OFF, FORMAT JSON) "+sql).Scan(&plans); err != nil {
			t.Fatal(err)
		}
		return nodes(plans[0]["Plan"].(planNode))
	}

	batches := func() any {
		for _, n := range explain("SELECT count(*) FROM orders o JOIN customers c ON c.id = o.customer_id") {
			if n["Node Type"] == "Hash" {
				return n["Hash Batches"]
			}
		}
		return nil
	}
	if b := batches(); b != 1.0 {
		t.Fatal("batches with the default work_mem:", b)
	}
	db.Exec(ctx, "SET work_mem = '64kB'")
	if b := batches(); b != 16.0 {
		t.Fatal("batches with 64kB:", b)
	}
	db.Exec(ctx, "RESET work_mem")

	query := "SELECT * FROM addresses WHERE city = 'London' AND country = 'UK'"
	if top := explain(query)[0]; top["Plan Rows"] != 900.0 || top["Actual Rows"] != 3000.0 {
		t.Fatal(top["Plan Rows"], top["Actual Rows"])
	}
	db.Exec(ctx, "CREATE STATISTICS addresses_city_country (dependencies) ON city, country FROM addresses")
	db.Exec(ctx, "ANALYZE addresses")
	if top := explain(query)[0]; top["Plan Rows"] != 3000.0 {
		t.Fatal(top["Plan Rows"])
	}

	offset := explain("SELECT * FROM orders ORDER BY id OFFSET 100000 LIMIT 20")
	keyset := explain("SELECT * FROM orders WHERE id > 100000 ORDER BY id LIMIT 20")
	if offset[1]["Actual Rows"] != 100020.0 || keyset[1]["Actual Rows"] != 20.0 {
		t.Fatal(offset[1]["Actual Rows"], keyset[1]["Actual Rows"])
	}
}
