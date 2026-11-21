// Checks.
static void Check(bool ok, object? detail)
{
    if (!ok) throw new Exception($"check failed: {detail}");
}
static double Round2(double x) => Math.Round(x, 2, MidpointRounding.AwayFromZero);
static Func<string, string> WithChange(string part, string label) => t => t.Contains(part) ? label : Evals.Keywords(t);

var golden = Evals.LoadGolden(Path.Combine(args.Length > 0 ? args[0] : "../shared", "golden.jsonl"));
Check(golden.Count == 20, golden.Count);

Check(Evals.ParseLabel("Category: BUG") == "bug" && Evals.ParseLabel("bug or billing") is null, "ParseLabel");
var (low, high) = Evals.Wilson(17, 20);
Check((Round2(low), Round2(high)) == (0.64, 0.95), (low, high));

Check(Evals.RunEval(Evals.Majority(golden), golden).Passed == 8, "majority");
var rules = Evals.RunEval(Evals.Keywords, golden);
var misses = rules.Results.Where(r => !r.Pass).Select(r => $"{r.Id}:{r.Got}").ToList();
Check(rules.Passed == 15 && misses.SequenceEqual(["t10:other", "t12:other", "t14:other", "t15:feature", "t20:billing"]),
    string.Join(" ", misses));
Check(rules.ByTag["other-language"] == (0, 2), rules.ByTag["other-language"]);

var (fixedIds, brokeIds) = Evals.Compare(rules, Evals.RunEval(WithChange("La aplicación", "bug"), golden));
Check(fixedIds.SequenceEqual(["t14"]) && brokeIds.Count == 0, string.Join(",", fixedIds));
var worse = Evals.RunEval(WithChange("charged twice", "bug"), golden);
Check(Evals.Gate(rules, 0.6).Count == 0, "base passes");
var reasons = Evals.Gate(worse, 0.75, rules, "t02", "t18");
Check(reasons.SequenceEqual(["pass rate 70% is below the floor of 75%", "regressed on t02", "must-pass case t02 failed"]),
    string.Join(" | ", reasons));

Check(Evals.Pairwise(_ => "FIRST", "ticket", "reply A", "reply B") == "inconsistent", "biased");
Check(Evals.Pairwise(p => p.IndexOf("reply B") < p.IndexOf("reply A") ? "FIRST" : "SECOND", "ticket", "reply A", "reply B") == "b", "fair");

bool[] human = [true, true, false, false, true, false, true, false, false, true];
bool[] lenient = [true, true, true, true, true, true, true, true, false, true];
var (agree, kappa) = Evals.Agreement(lenient, human);
Check((Round2(agree), Round2(kappa)) == (0.6, 0.2), (agree, kappa));

Console.WriteLine("ok: the same 8/20, 15/20, gate reasons and kappa as every other language");
