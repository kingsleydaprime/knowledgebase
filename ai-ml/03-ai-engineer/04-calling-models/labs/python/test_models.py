import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from models import Conversation, FakeModel, ModelError, OpenAICompatibleModel, sse_data


class FakeServer:
    """A real HTTP server on a free port: records requests, answers with canned (status, body) pairs.
    Headers are kept as the server parsed them, so lookups ignore case, as HTTP does."""

    def __init__(self, *responses: tuple[int, bytes]):
        self.responses, self.requests = list(responses), []
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                body = self.rfile.read(int(self.headers["content-length"]))
                fake.requests.append({"path": self.path, "headers": self.headers, "body": json.loads(body)})
                self._reply()

            def do_GET(self):
                fake.requests.append({"path": self.path, "headers": self.headers, "body": None})
                self._reply()

            def _reply(self):
                status, body = fake.responses.pop(0)
                self.send_response(status)
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *_):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self.server.serve_forever, args=(0.01,), daemon=True).start()
        self.url = f"http://127.0.0.1:{self.server.server_port}/v1"

    def close(self):
        self.server.shutdown()
        self.server.server_close()


def ok(obj) -> tuple[int, bytes]:
    return 200, json.dumps(obj).encode()


class ModelTests(unittest.TestCase):
    def serve(self, *responses):
        server = FakeServer(*responses)
        self.addCleanup(server.close)
        return server, OpenAICompatibleModel(server.url, "some-model", api_key="sk-test")

    def test_chat_sends_the_messages_format_and_reads_text_finish_reason_and_usage(self):
        server, model = self.serve(ok({"choices": [{"message": {"content": "Paris"}, "finish_reason": "stop"}],
                                       "usage": {"prompt_tokens": 21, "completion_tokens": 2}}))
        result = model.chat([{"role": "user", "content": "Capital of France?"}], temperature=0, max_tokens=5)

        self.assertEqual((result.text, result.finish_reason, result.input_tokens, result.output_tokens), ("Paris", "stop", 21, 2))
        req = server.requests[0]
        self.assertEqual(req["path"], "/v1/chat/completions")
        self.assertEqual(req["headers"]["authorization"], "Bearer sk-test")
        self.assertEqual(req["body"], {"model": "some-model", "messages": [{"role": "user", "content": "Capital of France?"}],
                                       "stream": False, "temperature": 0, "max_tokens": 5})

    def test_a_reply_cut_off_by_max_tokens_says_so(self):
        _, model = self.serve(ok({"choices": [{"message": {"content": "The capital of"}, "finish_reason": "length"}]}))
        self.assertEqual(model.chat([]).finish_reason, "length")

    def test_errors_carry_the_status_and_whether_a_retry_could_help(self):
        _, model = self.serve((429, b"slow down"), (400, b"bad model name"))
        with self.assertRaises(ModelError) as rate_limited:
            model.chat([])
        self.assertEqual((rate_limited.exception.status, rate_limited.exception.retryable), (429, True))
        with self.assertRaises(ModelError) as bad_request:
            model.chat([])
        self.assertEqual((bad_request.exception.status, bad_request.exception.retryable), (400, False))

    def test_the_sse_reader_survives_events_split_across_chunks_even_mid_character(self):
        chunks = [b'data: {"a":1}\n\nda', b'ta: {"b":"caf\xc3', b'\xa9"}\n\ndata: [DONE]\n\ndata: {"ignored":true}\n\n']
        self.assertEqual(list(sse_data(chunks)), ['{"a":1}', '{"b":"café"}'])  # "é" is 0xC3 0xA9, split in two

    def test_stream_yields_the_text_deltas_in_order(self):
        delta = lambda text: f"data: {json.dumps({'choices': [{'delta': {'content': text}}]})}\n\n"
        server, model = self.serve((200, (delta("Hel") + delta("lo") + delta(", world") + "data: [DONE]\n\n").encode()))
        self.assertEqual(list(model.stream([{"role": "user", "content": "hi"}])), ["Hel", "lo", ", world"])
        self.assertIs(server.requests[0]["body"]["stream"], True)

    def test_list_models_asks_the_server_instead_of_trusting_memory(self):
        server, model = self.serve(ok({"data": [{"id": "qwen3.5:4b"}, {"id": "gemma4:latest"}]}))
        self.assertEqual(model.list_models(), ["gemma4:latest", "qwen3.5:4b"])
        self.assertEqual(server.requests[0]["path"], "/v1/models")

    def test_the_model_is_stateless_so_a_conversation_resends_every_turn(self):
        model = FakeModel(["Hi Kingsley.", "Your name is Kingsley."])
        chat = Conversation(model, "Be brief.")
        chat.say("My name is Kingsley.")
        self.assertEqual(chat.say("What's my name?"), "Your name is Kingsley.")
        self.assertEqual(len(model.calls[0]), 2)
        self.assertEqual([m["role"] for m in model.calls[1]], ["system", "user", "assistant", "user"])


if __name__ == "__main__":
    unittest.main()
