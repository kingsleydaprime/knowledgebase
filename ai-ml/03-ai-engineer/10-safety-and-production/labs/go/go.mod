module safety

go 1.26.0

require (
	evals v0.0.0
	tools v0.0.0
)

require github.com/google/jsonschema-go v0.4.3

replace (
	evals => ../../../12-evals/labs/go
	tools => ../../../07-tools-and-mcp/labs/go
)
