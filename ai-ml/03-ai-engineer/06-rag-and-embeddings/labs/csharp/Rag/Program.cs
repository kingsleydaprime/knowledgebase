// Checks: the same rankings, scores and metrics as every other language.
using System.Globalization;

static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}

static string Rounded(IEnumerable<Scored> ranked) => string.Join(" ", ranked.Select(r => string.Create(CultureInfo.InvariantCulture, $"{r.Id}:{r.Score:F4}")));

var shared = args.Length > 0 ? args[0] : "../shared";
var docs = Rag.LoadDocs(Path.Combine(shared, "help.json"));
var items = docs.SelectMany(d => Rag.ChunkDoc(d).Select(c => new Item(c.Id, Rag.WithContext(c, d.Title)))).ToList();
Check(items.Select(i => i.Id).SequenceEqual(["refunds#1", "refunds#2", "refunds#3", "password#1", "password#2", "export#1", "export#2", "appearance#1", "shipping#1", "shipping#2"]), "chunk ids");
Check(items[1].Text == "Refunds > How long a refund takes\nMost refunds arrive within 5 to 10 working days. Your bank may take a few more days to show it.", items[1].Text);
var longDoc = Rag.ChunkDoc(new Doc("long", "Long", "## Part\none two three four\n\nfive six seven eight\n\nnine ten eleven twelve"), 8);
Check(longDoc[1].Text == "five six seven eight\n\nnine ten eleven twelve", "overlap");

Check(Rag.Cosine([1, 0], [5, 0]) == 1 && Rag.Cosine([1, 0], [0, 1]) == 0 && Math.Round(Rag.Cosine([1, 0], [1, 1]), 3) == 0.707 && Rag.Cosine([0, 0], [1, 1]) == 0, "cosine");
Check(Rag.ToyEmbed("My login doesn't work any more.").SequenceEqual([1.0, 0, 0, 0, 0, 0]), "toy embed");

var k = Rag.BM25("My login doesn't work any more.", items);
var v = Rag.VectorSearch("My login doesn't work any more.", items, Rag.ToyEmbed);
Check(Rounded(k) == "refunds#2:1.8951 refunds#1:1.6952" && Rounded(v) == "password#1:0.9864 password#2:0.9701", $"{Rounded(k)} | {Rounded(v)}");
Check(Rag.RRF(k, v).Select(s => s.Id).SequenceEqual(["refunds#2", "password#1", "refunds#1", "password#2"]), "rrf");
Check(Rounded(Rag.BM25("What does E1042 mean?", items)) == "export#2:2.8115", "E1042");
Check(Rounded(Rag.BM25("Can I make the app darker?", items).Take(3)) == "refunds#1:1.8249 appearance#1:1.2348 password#2:1.1894", "darker");

var questions = Rag.LoadQuestions(Path.Combine(shared, "questions.json"));
var results = new Dictionary<string, Dictionary<string, List<string>>> { ["keyword"] = [], ["vector"] = [], ["hybrid"] = [] };
foreach (var q in questions)
{
    var (kq, vq) = (Rag.BM25(q.Text, items), Rag.VectorSearch(q.Text, items, Rag.ToyEmbed));
    (results["keyword"][q.Id], results["vector"][q.Id], results["hybrid"][q.Id]) = (Rag.DocsOf(kq), Rag.DocsOf(vq), Rag.DocsOf(Rag.RRF(kq, vq)));
}
foreach (var (name, want) in new[] { ("keyword", "0.6 0.8 0.700"), ("vector", "0.8 0.8 0.800"), ("hybrid", "0.8 1 0.900") })
{
    var r = results[name];
    var got = string.Create(CultureInfo.InvariantCulture, $"{Rag.RecallAtK(r, questions, 1)} {Rag.RecallAtK(r, questions, 3)} {Rag.MRR(r, questions):F3}");
    Check(got == want, $"{name}: {got}");
}

Check(Rag.GroundedPrompt("How long?", [("refunds#2", "Most refunds arrive within 5 to 10 working days.")]).Contains("[S1] (refunds#2)\nMost refunds arrive within 5 to 10 working days."), "prompt");
Check(Rag.CheckCitations("Within 5 to 10 working days [S1].", 2).Count == 0 && Rag.CheckCitations("I don't know.", 2).Count == 0, "ok");
Check(Rag.CheckCitations("Refunds are instant.", 2).SequenceEqual(["no citations"]), "none");
Check(Rag.CheckCitations("A week [S3].", 2).SequenceEqual(["cites S3, which wasn't given"]), "invented");

Console.WriteLine("all RAG checks passed");
