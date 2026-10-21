# AFI Academy plugin

Lets you create AFI Academy training courses by talking to Claude.

## Set up (once)

You can ask Claude to do steps 1 to 3 for you: "Install the AFI Academy plugin from https://github.com/American-Foods-intl/afi-academy-plugin.git".
Claude shows each command and asks before it runs it.

1. The plugin needs `uv`. If it isn't installed, follow https://docs.astral.sh/uv/getting-started/installation/
   (one command on Mac or Windows), or ask Claude to install it.
2. If you connected Claude to the Academy by hand before (a `claude mcp add afi-academy ...` command),
   remove that first: `claude mcp remove afi-academy`
3. Install the plugin. In Claude Code run:
   `/plugin marketplace add https://github.com/American-Foods-intl/afi-academy-plugin.git`
   then `/plugin install afi-academy@afi-academy-plugin`.
4. Open the Academy, go to **Me → Connect Claude**. The page shows the exact command for Mac and for Windows.
   Copy it into Terminal (Mac) or PowerShell (Windows) and run it. This saves your personal key on your computer.
   The key is yours alone: never share it, paste it in chat or email it.
5. Restart Claude Code. The first start takes about a minute while the plugin sets itself up.

## Use it

Type `/afi-course` (or `/afi-academy:afi-course`) and Claude will interview you,
write a draft course and save it in the Academy for review.
