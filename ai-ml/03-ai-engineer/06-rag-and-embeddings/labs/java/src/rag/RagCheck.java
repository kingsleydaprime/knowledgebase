package rag;

import java.nio.file.Path;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.stream.Collectors;
import rag.Rag.Item;
import rag.Rag.Scored;
import rag.Rag.Source;

/** Checks, run with `java -ea`. The same rankings, scores and metrics as every other language. */
public final class RagCheck {
    static void check(boolean ok, Object detail) {
        if (!ok) throw new AssertionError(detail);
    }

    static String rounded(List<Scored> ranked) {
        return ranked.stream().map(r -> String.format(Locale.ROOT, "%s:%.4f", r.id(), r.score())).collect(Collectors.joining(" "));
    }

    public static void main(String[] args) throws Exception {
        var docs = Rag.loadDocs(Path.of("..", "shared", "help.json"));
        var items = docs.stream().flatMap(d -> Rag.chunkDoc(d, 60).stream().map(c -> new Item(c.id(), Rag.withContext(c, d.title())))).toList();
        check(items.stream().map(Item::id).toList().equals(List.of("refunds#1", "refunds#2", "refunds#3", "password#1", "password#2",
                "export#1", "export#2", "appearance#1", "shipping#1", "shipping#2")), "chunk ids");
        check(items.get(1).text().equals("Refunds > How long a refund takes\nMost refunds arrive within 5 to 10 working days. Your bank may take a few more days to show it."), items.get(1));
        var longDoc = Rag.chunkDoc(new Rag.Doc("long", "Long", "## Part\none two three four\n\nfive six seven eight\n\nnine ten eleven twelve"), 8);
        check(longDoc.get(1).text().equals("five six seven eight\n\nnine ten eleven twelve"), "overlap");

        check(Rag.cosine(new double[] {1, 0}, new double[] {5, 0}) == 1 && Rag.cosine(new double[] {1, 0}, new double[] {0, 1}) == 0
                && Math.round(Rag.cosine(new double[] {1, 0}, new double[] {1, 1}) * 1000) / 1000.0 == 0.707, "cosine");
        check(java.util.Arrays.equals(Rag.toyEmbed("My login doesn't work any more."), new double[] {1, 0, 0, 0, 0, 0}), "toy embed");

        var k = Rag.bm25("My login doesn't work any more.", items);
        var v = Rag.vectorSearch("My login doesn't work any more.", items, Rag::toyEmbed);
        check(rounded(k).equals("refunds#2:1.8951 refunds#1:1.6952") && rounded(v).equals("password#1:0.9864 password#2:0.9701"), rounded(k) + " | " + rounded(v));
        check(Rag.rrf(k, v).stream().map(Scored::id).toList().equals(List.of("refunds#2", "password#1", "refunds#1", "password#2")), "rrf");
        check(rounded(Rag.bm25("What does E1042 mean?", items)).equals("export#2:2.8115"), "E1042");
        check(rounded(Rag.bm25("Can I make the app darker?", items).subList(0, 3)).equals("refunds#1:1.8249 appearance#1:1.2348 password#2:1.1894"), "darker");

        var questions = Rag.loadQuestions(Path.of("..", "shared", "questions.json"));
        Map<String, Map<String, List<String>>> results = Map.of("keyword", new HashMap<>(), "vector", new HashMap<>(), "hybrid", new HashMap<>());
        for (var q : questions) {
            var kq = Rag.bm25(q.question(), items);
            var vq = Rag.vectorSearch(q.question(), items, Rag::toyEmbed);
            results.get("keyword").put(q.id(), Rag.docsOf(kq));
            results.get("vector").put(q.id(), Rag.docsOf(vq));
            results.get("hybrid").put(q.id(), Rag.docsOf(Rag.rrf(kq, vq)));
        }
        for (var e : Map.of("keyword", "0.6 0.8 0.700", "vector", "0.8 0.8 0.800", "hybrid", "0.8 1.0 0.900").entrySet()) {
            var r = results.get(e.getKey());
            String got = String.format(Locale.ROOT, "%.1f %.1f %.3f", Rag.recallAtK(r, questions, 1), Rag.recallAtK(r, questions, 3), Rag.mrr(r, questions));
            check(got.equals(e.getValue()), e.getKey() + ": " + got);
        }

        check(Rag.groundedPrompt("How long?", List.of(new Source("refunds#2", "Most refunds arrive within 5 to 10 working days.")))
                .contains("[S1] (refunds#2)\nMost refunds arrive within 5 to 10 working days."), "prompt");
        check(Rag.checkCitations("Within 5 to 10 working days [S1].", 2).isEmpty() && Rag.checkCitations("I don't know.", 2).isEmpty(), "ok");
        check(Rag.checkCitations("Refunds are instant.", 2).equals(List.of("no citations")), "none");
        check(Rag.checkCitations("A week [S3].", 2).equals(List.of("cites S3, which wasn't given")), "invented");

        System.out.println("all RAG checks passed");
    }
}
