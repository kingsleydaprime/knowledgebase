# Record ID Generator — Lombok & Configuration

Split out from the original single-file `learning.md`. Covers Lombok's `@Data` annotation and
Java properties-file configuration. See also `01-java-fundamentals.md` and
`02-build-tools-and-architecture.md`.

---

## 6. Lombok — Less Boilerplate

Java requires you to write getters and setters manually for every field. For a class like `Transaction` with 25 fields, this is brutal.

Here is what even a **trimmed-down** version of `Transaction` looks like without Lombok — just 5 of the 25 fields:

```java
public class Transaction {
    private String id;
    private String sourceHash;
    private String paymentTypeId;
    private BigDecimal amount;
    private LocalDateTime sourceDateCreated;

    // Constructor
    public Transaction() {}

    // Getters
    public String getId() { return id; }
    public String getSourceHash() { return sourceHash; }
    public String getPaymentTypeId() { return paymentTypeId; }
    public BigDecimal getAmount() { return amount; }
    public LocalDateTime getSourceDateCreated() { return sourceDateCreated; }

    // Setters
    public void setId(String id) { this.id = id; }
    public void setSourceHash(String sourceHash) { this.sourceHash = sourceHash; }
    public void setPaymentTypeId(String paymentTypeId) { this.paymentTypeId = paymentTypeId; }
    public void setAmount(BigDecimal amount) { this.amount = amount; }
    public void setSourceDateCreated(LocalDateTime sourceDateCreated) {
        this.sourceDateCreated = sourceDateCreated;
    }

    // toString — so you can print the object
    @Override
    public String toString() {
        return "Transaction{id='" + id + "', sourceHash='" + sourceHash +
               "', paymentTypeId='" + paymentTypeId + "', amount=" + amount +
               ", sourceDateCreated=" + sourceDateCreated + "}";
    }

    // equals — so two Transaction objects with the same data are considered equal
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Transaction)) return false;
        Transaction t = (Transaction) o;
        return Objects.equals(id, t.id) && Objects.equals(amount, t.amount);
        // ... and every other field
    }

    // hashCode — needed whenever you override equals
    @Override
    public int hashCode() {
        return Objects.hash(id, sourceHash, paymentTypeId, amount, sourceDateCreated);
    }
}
```

That is ~50 lines for **5 fields**. The actual `Transaction` has 25 fields. Without Lombok, the full class would be **over 200 lines** of code that carries zero business logic — it just moves data around.

Now the same class with Lombok:

```java
import lombok.Data;

@Data
public class Transaction {
    private String id;
    private String sourceHash;
    private String paymentTypeId;
    private String sourceId;
    private String thirdpartyId;
    private LocalDateTime sourceDateCreated;
    private String sourceAccountNo;
    private String sourceTransId;
    private String channelId;
    private String terminalId;
    private String merchantId;
    private String productId;
    private String subMerchantId;
    private String accountref;
    private String accountname;
    private String paymentmsisdn;
    private String narration;
    private String currency;
    private BigDecimal amount;
    private BigDecimal fees;
    private int year;
    private String processor;
    private String country;
    private String transtype;
    private String month;
}
```

`@Data` generates at compile time:
- A getter for every field (`getId()`, `getAmount()`, etc.)
- A setter for every non-final field (`setId()`, `setAmount()`, etc.)
- `toString()` — prints all field values
- `equals()` and `hashCode()` — based on all fields
- A required-args constructor

The 200+ line manual version becomes 28 lines. No getters to forget, no `toString()` to keep in sync when you add a field — Lombok regenerates everything automatically every time you build.

**How it works**: Lombok hooks into the Java compiler as an annotation processor. It reads `@Data` and injects the bytecode before compilation finishes. There is no runtime dependency — Lombok is only needed at compile time (`compileOnly` in Gradle).

---

## 7. Configuration — Properties Files

Java convention for config:

```properties
# application.properties — safe to commit (no secrets)
db.url=jdbc:mysql://localhost:3306/itc_db
rabbitmq.host=localhost
rabbitmq.port=5672
file.path=/data/transactions.csv
```

```properties
# application-local.properties — GITIGNORED (secrets)
db.user=itc
db.password=itc
rabbitmq.user=guest
rabbitmq.pass=guest
```

Reading in Java:
```java
Properties props = new Properties();
try (InputStream in = MyClass.class.getClassLoader()
        .getResourceAsStream("application.properties")) {
    props.load(in);
}
String url = props.getProperty("db.url");
```

---

