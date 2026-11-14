// Open: a dictionary of delegates. Closed: an enum and a switch expression, where the compiler
// warns (CS8509) about an unhandled value — an error here, because warnings are errors.
var openRules = new Dictionary<string, Func<long, long>>
{
    ["card"] = amount => amount * 29 / 1000,
    ["transfer"] = _ => 50,
};

if (openRules["card"](10_000) != 290 || Fee(Method.Card, 10_000) != 290 || Fee(Method.Transfer, 10_000) != 50)
    throw new Exception("FAIL: designs disagree");
Console.WriteLine("ok: delegate dictionary and enum switch agree");

// CS8524 is about integers cast to Method that aren't named values — not what this lab checks.
#pragma warning disable CS8524
static long Fee(Method method, long amountKobo) => method switch
{
    Method.Card => amountKobo * 29 / 1000,
    Method.Transfer => 50,
};
#pragma warning restore CS8524

enum Method { Card, Transfer }
