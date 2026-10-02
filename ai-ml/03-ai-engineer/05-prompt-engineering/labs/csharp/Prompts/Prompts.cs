// Prompts as files, shared with every other language's lab, rendered with Handlebars.Net.
using System.Text.Json;
using System.Text.RegularExpressions;
using HandlebarsDotNet;

public record Example(string Review, string Label);

public record Reviews(List<Example> Examples, List<Example> Cases);

public record Failure(string Review, string Expected, string? Got, string Reply);

public record Score(int Correct, int Total, List<Failure> Failures);

public static partial class Prompts
{
    public static string Shared = "../shared"; // the container runs from a copy, so this can be changed

    /// <summary>Handlebars was built for HTML: by default it escapes "&amp;" and quotes, and renders a
    /// missing value as "". A prompt needs neither, so switch both off.</summary>
    static readonly IHandlebars Handlebars = HandlebarsDotNet.Handlebars.Create(new HandlebarsConfiguration
    {
        NoEscape = true,
        ThrowOnUnresolvedBindingExpression = true,
    });

    public static string Render(string name, Dictionary<string, string> values) =>
        Handlebars.Compile(File.ReadAllText(Path.Combine(Shared, "prompts", name + ".md")))(values);

    [GeneratedRegex("</?review>", RegexOptions.IgnoreCase)]
    private static partial Regex ReviewTag();

    /// <summary>Stops user text from closing the &lt;review&gt; tag early. Lowers injection risk; doesn't remove it.</summary>
    public static string FenceUserText(string text) => ReviewTag().Replace(text, m => "&lt;" + m.Value[1..]);

    /// <summary>Few-shot examples in exactly the format of the real question.</summary>
    public static string FormatExamples(IEnumerable<Example> examples) =>
        string.Join("\n\n", examples.Select(e => $"<review>\n{FenceUserText(e.Review)}\n</review>\n{e.Label}"));

    [GeneratedRegex(@"\b(positive|negative|mixed)\b")]
    private static partial Regex Label();

    /// <summary>Accepts "Mixed." or "Sentiment: positive"; rejects replies naming two different labels.</summary>
    public static string? ParseLabel(string reply)
    {
        var found = Label().Matches(reply.ToLowerInvariant()).Select(m => m.Value).Distinct().ToList();
        return found.Count == 1 ? found[0] : null;
    }

    public static Reviews LoadReviews() =>
        JsonSerializer.Deserialize<Reviews>(File.ReadAllText(Path.Combine(Shared, "reviews.json")),
            new JsonSerializerOptions { PropertyNameCaseInsensitive = true })!;

    /// <summary>Scores a prompt against labelled cases, so "this wording feels better" becomes a number.</summary>
    public static Score Evaluate(Func<string, string> ask, string prompt, List<Example> cases, List<Example> examples)
    {
        var failures = new List<Failure>();
        foreach (var c in cases)
        {
            var values = new Dictionary<string, string> { ["review"] = FenceUserText(c.Review) };
            if (prompt == "classify-few-shot") values["examples"] = FormatExamples(examples);
            var reply = ask(Render(prompt, values));
            var got = ParseLabel(reply);
            if (got != c.Label) failures.Add(new(c.Review, c.Label, got, reply));
        }
        return new(cases.Count - failures.Count, cases.Count, failures);
    }
}
