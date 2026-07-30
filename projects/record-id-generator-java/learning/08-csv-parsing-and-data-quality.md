# Record ID Generator — CSV Parsing at Scale

Split out from the original single-file `learning.md`. Covers streaming a 1.46GB CSV with
`BufferedReader` and the quoted-comma bug that breaks naive `split(",")` parsing.

---

## 12. CSV Parsing at Scale

For a 1.46GB file, never load it all into memory. Read line by line:

```java
BufferedReader reader = new BufferedReader(new FileReader(filePath))
```

`BufferedReader` reads chunks into a buffer — much faster than reading byte by byte.

```java
String line;
boolean isHeader = true;
while ((line = reader.readLine()) != null) {
    if (isHeader) { isHeader = false; continue; } // skip header row
    channel.basicPublish("", queueName, null, line.getBytes());
}
```

### Parsing a CSV line

```java
String[] fields = line.replace("\"", "").split(",");
// "MOMO","MTN","123" → after replace → MOMO,MTN,123 → split → [MOMO, MTN, 123]
```

Map to object by index (order matches CSV column order):
```java
t.setPaymentTypeId(fields[0]);
t.setSourceId(fields[1]);
t.setAmount(new BigDecimal(fields[16]));
```

### The Quoted Comma Bug — Why split(",") Is Not Enough

The approach above has a silent failure mode. Consider a CSV row where one field contains a comma inside quotes:

```
"MOMO","MTN","TXN001","2024-01-01 00:00:00","ACC","SRC","MOB","TERM","MERCH","PROD","SUB","REF","Smith, John","0244000000","Payment","GHS",50.00,2.50,2024,"MTN","Ghana","TRANSFER","JAN"
```

After `line.replace("\"", "")`, the quotes are gone:
```
MOMO,MTN,TXN001,2024-01-01 00:00:00,ACC,SRC,MOB,TERM,MERCH,PROD,SUB,REF,Smith, John,0244000000,Payment,GHS,50.00,...
```

Now `split(",")` sees the comma inside `Smith, John` as a field separator. Every field from index 13 onwards shifts by one. What was `fields[16]` (amount = `50.00`) is now `fields[17]` (currency = `GHS`). When the code calls `new BigDecimal("GHS")`, Java throws:

```
Character G is neither a decimal digit number, decimal point, nor "e" notation exponential mark.
```

The message gets nacked to the DLQ. The record never makes it to the database.

The fix is a proper CSV parser that tracks whether you're inside quotes:

```java
private String[] splitCsv(String line) {
    List<String> fields = new ArrayList<>();
    StringBuilder current = new StringBuilder();
    boolean inQuotes = false;
    for (char c : line.toCharArray()) {
        if (c == '"') {
            inQuotes = !inQuotes;        // toggle quote state
        } else if (c == ',' && !inQuotes) {
            fields.add(current.toString().trim());
            current.setLength(0);        // reset for next field
        } else {
            current.append(c);
        }
    }
    fields.add(current.toString().trim()); // last field (no trailing comma)
    return fields.toArray(new String[0]);
}
```

Then `parseLine` becomes:
```java
String[] fields = splitCsv(line);  // was: line.replace("\"", "").split(",")
```

Commas inside quotes are now preserved as part of the field value. The field count is always correct regardless of what the data contains.

This is a very common bug in data pipelines. Any time you see `split(",")` on a CSV line, ask: can any field value contain a comma? If yes — and in real-world data it almost always can (names, addresses, narrations) — the simple split will break silently on those rows.

---

