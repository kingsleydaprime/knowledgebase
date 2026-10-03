package architecture;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;

/** The arithmetic behind choosing a monolith, microservices or serverless, and a boundary checker. */
public final class Architecture {
    private Architecture() {}

    public static long coordinationLinks(long people) {
        return people * (people - 1) / 2;
    }

    public static double releaseBreaks(int changes, double p) {
        return 1 - Math.pow(1 - p, changes);
    }

    public record Extracted(double addedMs, double availability) {}

    public static Extracted extract(int callsPerRequest, double networkMs, double callAvailability) {
        return new Extracted(callsPerRequest * networkMs, Math.pow(callAvailability, callsPerRequest));
    }

    public record Pricing(double perMillionRequests, double perGbSecond) {}

    public static double serverlessMonthly(double requests, double ms, double memoryGb, Pricing p) {
        return requests / 1e6 * p.perMillionRequests() + requests * (ms / 1000) * memoryGb * p.perGbSecond();
    }

    public static double breakEvenRequests(double serverMonthly, double ms, double memoryGb, Pricing p) {
        return serverMonthly / (p.perMillionRequests() / 1e6 + (ms / 1000) * memoryGb * p.perGbSecond());
    }

    public static double coldShare(double perMinute, double warmMinutes) {
        return Math.exp(-perMinute * warmMinutes);
    }

    public static double simulateColdShare(double perMinute, double warmMinutes, int requests, int seed) {
        int a = seed;
        int cold = 0;
        for (int i = 0; i < requests; i++) {
            a += 0x6d2b79f5; // mulberry32, as in week 1's lab
            int t = (a ^ (a >>> 15)) * (a | 1);
            t ^= t + (t ^ (t >>> 7)) * (t | 61);
            double random = Integer.toUnsignedLong(t ^ (t >>> 14)) / 4294967296.0;
            if (-Math.log(1 - random) / perMinute > warmMinutes) cold++;
        }
        return (double) cold / requests;
    }

    public record Module(String name, List<String> imports) {}

    /** Imports that reach inside another module. JPMS modules, ArchUnit or Spring Modulith enforce this in real code. */
    public static List<String> boundaryViolations(List<Module> modules) {
        Set<String> names = modules.stream().map(Module::name).collect(Collectors.toSet());
        List<String> out = new ArrayList<>();
        for (Module m : modules) {
            for (String imp : m.imports()) {
                String target = imp.split("/")[0];
                if (!target.equals(m.name()) && names.contains(target) && imp.contains("/")) out.add(m.name() + " → " + imp);
            }
        }
        return out;
    }

    public static Optional<List<String>> findCycle(List<Module> modules) {
        Map<String, Set<String>> deps = new LinkedHashMap<>();
        for (Module m : modules) {
            Set<String> ds = new LinkedHashSet<>();
            for (String imp : m.imports()) {
                String d = imp.split("/")[0];
                if (!d.equals(m.name())) ds.add(d);
            }
            deps.put(m.name(), ds);
        }
        Map<String, String> state = new HashMap<>();
        List<String> path = new ArrayList<>();
        for (Module m : modules) {
            var cycle = visit(m.name(), deps, state, path);
            if (cycle.isPresent()) return cycle;
        }
        return Optional.empty();
    }

    private static Optional<List<String>> visit(String name, Map<String, Set<String>> deps, Map<String, String> state, List<String> path) {
        if ("done".equals(state.get(name))) return Optional.empty();
        if ("visiting".equals(state.get(name))) {
            List<String> cycle = new ArrayList<>(path.subList(path.indexOf(name), path.size()));
            cycle.add(name); // back to a module on the path
            return Optional.of(cycle);
        }
        state.put(name, "visiting");
        path.add(name);
        for (String d : deps.getOrDefault(name, Set.of())) {
            var cycle = visit(d, deps, state, path);
            if (cycle.isPresent()) return cycle;
        }
        path.removeLast();
        state.put(name, "done");
        return Optional.empty();
    }
}
