---
id: 9de5f4cd-e124-4abb-8913-3834de9e602a
---

# Gin

Gin is a web framework for Go that gives you routing, request binding and validation in one package. Where Chi stays out of your way, Gin hands you its own `*gin.Context` and a set of helpers, and in return your handlers belong to Gin.

## A Gin server
<!-- bite: 3cbf346b-400c-4d6f-9ea0-5460c3db603a -->

```go
import "github.com/gin-gonic/gin"

r := gin.Default()                      // Logger + Recovery already attached

r.GET("/users/:id", func(c *gin.Context) {
    id := c.Param("id")
    filter := c.Query("filter")

    var req CreateUser
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    c.JSON(http.StatusOK, user)
})

api := r.Group("/api/v1", AuthMiddleware())
{
    api.GET("/users", listUsers)
    api.POST("/users", createUser)
}

r.Run(":8080")
```

Gin uses **its own context type**, `*gin.Context`, which carries the request, response, params, bound data, errors, and per-request key/value storage.

That's the trade. You get:

```go
c.JSON(200, obj)                        // marshal + content-type + status
c.ShouldBindJSON(&req)                  // decode + VALIDATE via struct tags
c.AbortWithStatusJSON(401, gin.H{...})  // stop the chain
c.Set("user", u); c.MustGet("user")     // request-scoped storage
c.ClientIP()                            // parses X-Forwarded-For
```

Binding with validation is the genuinely useful part:

```go
type CreateUser struct {
    Email string `json:"email" binding:"required,email"`
    Age   int    `json:"age"   binding:"gte=0,lte=130"`
}
```

One call decodes and validates, and returns a structured error. In stdlib Go you write that yourself.

And you lose: **handlers are no longer `http.HandlerFunc`.** Gin middleware is `gin.HandlerFunc`. Neither is portable, so adopting Gin is a decision about the whole codebase, not one route.

Gin does provide `gin.WrapH(h http.Handler)` and `gin.WrapF` to mount stdlib handlers, so the boundary is crossable in one direction.

---

## Related
<!-- bite: 25fbcc6c-e1bc-424d-ab56-fec921d96636 -->
- [[backend/frameworks/chi/01-chi|Chi]] — the other router, and the full stdlib / Chi / Gin comparison
- [[backend/frameworks/net-http/01-what-net-http-is-and-a-first-server|net/http in Depth]] — what Gin sits on
- [[backend/frameworks/net-http/03-middleware|Middleware as Composition]] — the portable middleware Gin gives up
- [[backend/frameworks/gin/index|Gin]]

## About this lesson
<!-- bite: 50e2bdd6-c902-4226-b5de-d61e4604fe7f -->

**Level:** Intermediate. **Covers:** What a Gin server looks like, what `*gin.Context` gives you, and what it costs you in portability.
