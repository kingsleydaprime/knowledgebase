# Setting up Neovim

To make neovim into an ide you need the following

- lsps
- formatters
- language syntax highlighters
- custom commands and suggestions
- format on save (optional)
## Setting up with NvChad distro

Note the following:

- for lsp config on neovim we will use `neovim/nvim-lspconfig`
- for installing the lsps we will use `williamboman/mason.nvim`,
- For syntax highlighting, we will use treesitter

### Adding plugins
You add plugins to this file `~/.config/nvim/lua/plugins/init.lua` or to the folder `~/.config/nvim/lua/plugins/init.lua`


### Configuring plugins
`~/.config/nvim/lua/plugins/init.lua`

#### Add mason
```lua
{
  "williamboman/mason.nvim",
  opts = {
    ensure_installed = {
      "pyright",          -- Python
      "tsserver",        -- TypeScript/JavaScript
      "clangd",          -- C/C++
      "rust_analyzer",   -- Rust
      "gopls",           -- Go
      "html",            -- HTML
      "cssls",           -- CSS
      "lua-language-server" -- Lua (for Neovim config)
    },
  },
},
```

#### Add treesitter
```lua
{
  "nvim-treesitter/nvim-treesitter",
  opts = {
    ensure_installed = {
      "python",
      "javascript",
      "typescript",
      "c",
      "cpp",
      "rust",
      "go",
      "html",
      "css",
      "lua"
    },
  },
},
```
> Run `:TSInstall python javascript typescript c cpp rust go html css lua` to install parsers.

#### Add conform.nvim
```lua
{
  "stevearc/conform.nvim",
  event = { "BufWritePre" },
  opts = {
    formatters_by_ft = {
      python = { "black" },
      javascript = { "prettier" },
      typescript = { "prettier" },
      c = { "clang_format" },
      cpp = { "clang_format" },
      rust = { "rustfmt" },
      go = { "gofmt" },
      html = { "prettier" },
      css = { "prettier" },
      lua = { "stylua" },
    },
    format_on_save = {
      timeout_ms = 500,
      lsp_fallback = true, -- Fallback to LSP if formatter fails
    },
  },
},
```
### Now to configure the lspconfig?

`~/.config/nvim/lua/configs/lspconfig.lua`
```lua
local lspconfig = require "lspconfig"
local nvlsp = require "nvchad.lsp"

-- List of servers
local servers = { "pyright", "tsserver", "clangd", "rust_analyzer", "gopls", "html", "cssls", "lua_ls" }

-- Default setup for each server
for _, lsp in ipairs(servers) do
  lspconfig[lsp].setup {
    on_attach = nvlsp.on_attach,
    on_init = nvlsp.on_init,
    capabilities = nvlsp.capabilities,
  }
end

-- Custom settings for specific servers
lspconfig.lua_ls.setup {
  on_attach = nvlsp.on_attach,
  capabilities = nvlsp.capabilities,
  settings = {
    Lua = {
      diagnostics = { globals = { "vim" } },
    },
  },
}

lspconfig.clangd.setup {
  on_attach = nvlsp.on_attach,
  capabilities = nvlsp.capabilities,
  cmd = { "clangd", "--background-index" },
  filetypes = { "c", "cpp", "objc", "objcpp" },
}
```
Enhance autocompletion and commands with `luasnip` and `cmp` in `~/.config/nvim/lua/configs/cmp.lua`

```lua
local cmp = require "cmp"
cmp.setup {
  snippet = {
	expand = function(args)
  	require("luasnip").lsp_expand(args.body) -- Snippet support
	End,
  },
  mapping = cmp.mapping.preset.insert {
	["<C-b>"] = cmp.mapping.scroll_docs(-4),
	["<C-f>"] = cmp.mapping.scroll_docs(4),
	["<C-Space>"] = cmp.mapping.complete(),
	["<C-e>"] = cmp.mapping.abort(),
	["<CR>"] = cmp.mapping.confirm { select = true },
  },
  sources = cmp.config.sources {
	{ name = "nvim_lsp" }, -- LSP completions
	{ name = "luasnip" },  -- Snippets
	{ name = "buffer" },   -- Buffer words
	{ name = "path" }, 	-- File paths
  },
}
```