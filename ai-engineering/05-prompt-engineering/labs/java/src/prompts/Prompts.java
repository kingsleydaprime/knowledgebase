package prompts;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.samskivert.mustache.Mustache;
import com.samskivert.mustache.Template;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.function.UnaryOperator;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

/** Prompts as files, shared with every other language's lab, rendered with Mustache (jmustache). */
public final class Prompts {
    private Prompts() {}

    static final Path SHARED = Path.of("..", "shared");

    /**
     * jmustache throws on a missing value by default, which is what a prompt needs. It also
     * HTML-escapes by default, which isn't: a review saying "fine" & cheap would reach the model
     * as &quot;fine&quot; &amp; cheap. escapeHTML(false) sends the text as written.
     */
    static final Mustache.Compiler MUSTACHE = Mustache.compiler().escapeHTML(false);

    public static String render(String name, Map<String, String> values) {
        try {
            Template template = MUSTACHE.compile(Files.readString(SHARED.resolve("prompts").resolve(name + ".md")));
            return template.execute(values);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    private static final Pattern REVIEW_TAG = Pattern.compile("</?review>", Pattern.CASE_INSENSITIVE);

    /** Stops user text from closing the <review> tag early. Lowers injection risk; doesn't remove it. */
    public static String fenceUserText(String text) {
        return REVIEW_TAG.matcher(text).replaceAll(m -> Matcher.quoteReplacement("&lt;" + m.group().substring(1)));
    }

    public record Example(String review, String label) {}

    /** Few-shot examples in exactly the format of the real question. */
    public static String formatExamples(List<Example> examples) {
        return examples.stream()
                .map(e -> "<review>\n" + fenceUserText(e.review()) + "\n</review>\n" + e.label())
                .collect(Collectors.joining("\n\n"));
    }

    private static final Pattern LABEL = Pattern.compile("\\b(positive|negative|mixed)\\b");

    /** Accepts "Mixed." or "Sentiment: positive"; rejects replies naming two different labels. */
    public static Optional<String> parseLabel(String reply) {
        Set<String> found = LABEL.matcher(reply.toLowerCase()).results().map(m -> m.group(1)).collect(Collectors.toSet());
        return found.size() == 1 ? Optional.of(found.iterator().next()) : Optional.empty();
    }

    public record Reviews(List<Example> examples, List<Example> cases) {}

    public static Reviews loadReviews() {
        try {
            return new ObjectMapper().readValue(SHARED.resolve("reviews.json").toFile(), Reviews.class);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    public record Failure(String review, String expected, String got, String reply) {}

    public record Result(int correct, int total, List<Failure> failures) {}

    /** Scores a prompt against labelled cases, so "this wording feels better" becomes a number. */
    public static Result evaluate(UnaryOperator<String> ask, String prompt, List<Example> cases, List<Example> examples) {
        List<Failure> failures = new ArrayList<>();
        for (Example c : cases) {
            Map<String, String> values = new HashMap<>(Map.of("review", fenceUserText(c.review())));
            if (prompt.equals("classify-few-shot")) values.put("examples", formatExamples(examples));
            String reply = ask.apply(render(prompt, values));
            Optional<String> got = parseLabel(reply);
            if (!got.equals(Optional.of(c.label()))) failures.add(new Failure(c.review(), c.label(), got.orElse(null), reply));
        }
        return new Result(cases.size() - failures.size(), cases.size(), failures);
    }
}
