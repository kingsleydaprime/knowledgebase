package rates;

import java.util.ArrayList;
import java.util.List;

public final class Check {
    public static void main(String[] args) {
        var api = new Rates.FlakyApi(2);
        List<String> log = new ArrayList<>();
        Rates.RateSource rates = Rates.logging(new Rates.Caching(new Rates.Retrying(api, 3)), log);

        assert rates.rate("GBP", "NGN") == 2000;
        assert rates.rate("GBP", "NGN") == 2000;
        assert api.calls == 3 : api.calls;
        assert log.equals(List.of("GBP->NGN = 2000", "GBP->NGN = 2000")) : log;
        System.out.println("ok: record decorators and a dynamic-proxy logger");
    }
}
