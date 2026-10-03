// server.ts — a real gRPC server and client for shop.proto, on a local port. proto-loader reads the .proto at run
// time; the alternative is to generate typed code from it ahead of time (protobuf-es, ts-proto), which most
// production services do.
import * as grpc from "@grpc/grpc-js";
import * as protoLoader from "@grpc/proto-loader";

const definition = protoLoader.loadSync(new URL("./shop.proto", import.meta.url).pathname, {
  longs: Number, // uint32 fits in a JavaScript number; 64-bit fields would need care
  defaults: true, // a field the sender left out reads as its zero value, as proto3 specifies
});
const shop = grpc.loadPackageDefinition(definition).shop as any;

const ORDERS = new Map([[1, { id: 1, customer: "Gbenga Ali", totalPence: 8996 }]]);

/** Starts the Orders service on a free port. `delayMs` makes GetSummary slow, to test deadlines. */
export async function startServer(options: { delayMs?: number } = {}) {
  const server = new grpc.Server();
  const seen = { cancelled: 0 }; // calls the server noticed the client had given up on
  server.addService(shop.v1.Orders.service, {
    async GetSummary(call: grpc.ServerUnaryCall<{ id: number }, unknown>, reply: grpc.sendUnaryData<unknown>) {
      if (options.delayMs) await new Promise((r) => setTimeout(r, options.delayMs));
      if (call.cancelled) {
        seen.cancelled++; // the client's deadline passed: don't do work nobody will read
        return;
      }
      const order = ORDERS.get(call.request.id);
      if (!order) return reply({ code: grpc.status.NOT_FOUND, details: `no order ${call.request.id}` });
      reply(null, order);
    },
    WatchOrder(call: grpc.ServerWritableStream<{ id: number }, unknown>) {
      for (const status of ["created", "paid", "shipped"]) call.write({ id: call.request.id, status });
      call.end();
    },
  });
  const port = await new Promise<number>((resolve, reject) =>
    server.bindAsync("127.0.0.1:0", grpc.ServerCredentials.createInsecure(), (err, p) => (err ? reject(err) : resolve(p))),
  );
  return { port, seen, stop: () => new Promise<void>((resolve) => server.tryShutdown(() => resolve())) };
}

/** A client for the same service. Insecure (no TLS) because it only ever talks to 127.0.0.1 in this lab. */
export function connect(port: number) {
  const client = new shop.v1.Orders(`127.0.0.1:${port}`, grpc.credentials.createInsecure());
  return {
    /** A unary call with a deadline: the moment after which the client stops waiting, and tells the server so. */
    getSummary(id: number, deadlineMs = 1_000): Promise<{ id: number; customer: string; totalPence: number }> {
      return new Promise((resolve, reject) =>
        client.GetSummary({ id }, { deadline: Date.now() + deadlineMs }, (err: grpc.ServiceError | null, res: any) => (err ? reject(err) : resolve(res))),
      );
    },
    /** A server stream, collected into a list. */
    watchOrder(id: number): Promise<string[]> {
      return new Promise((resolve, reject) => {
        const statuses: string[] = [];
        client.WatchOrder({ id }).on("data", (e: { status: string }) => statuses.push(e.status)).on("end", () => resolve(statuses)).on("error", reject);
      });
    },
    close: () => client.close(),
  };
}
