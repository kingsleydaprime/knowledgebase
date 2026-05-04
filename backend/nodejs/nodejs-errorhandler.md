# Ways to handle errors in nodejs

## Handling with process

```ts
process
  .on("uncaughtException", (err)=>{
    console.error(err)
  })
  .on("unhandledRejection", (err)=>{
    console.error(err)
  })
```

## Custom Express Error Handler

```ts
```