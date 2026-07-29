// Tool definitions handed to Gemini (via the OpenAI-compatible endpoint) plus
// the dispatcher that executes each call against the Tally proxy. Read-only.
import { tally } from "./tally";

export const tools = [
  {
    type: "function" as const,
    function: {
      name: "get_companies",
      description: "List the companies currently loaded in TallyPrime.",
      parameters: { type: "object", properties: {} },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "get_ledgers",
      description:
        "List all ledgers with their parent group and closing balance. Use for questions about accounts, balances, expenses, sales, cash, or bank.",
      parameters: { type: "object", properties: {} },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "get_ledger_balance",
      description: "Get the closing balance of a single ledger by its exact name.",
      parameters: {
        type: "object",
        properties: {
          name: { type: "string", description: 'Ledger name, e.g. "HDFC Bank Account"' },
        },
        required: ["name"],
      },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "get_receivables",
      description: "List Sundry Debtors (money owed TO the business) with balances.",
      parameters: { type: "object", properties: {} },
    },
  },
  {
    type: "function" as const,
    function: {
      name: "get_payables",
      description: "List Sundry Creditors (money the business OWES) with balances.",
      parameters: { type: "object", properties: {} },
    },
  },
];

export async function runTool(name: string, args: Record<string, unknown>): Promise<string> {
  try {
    switch (name) {
      case "get_companies":
        return JSON.stringify(await tally.companies());
      case "get_ledgers":
        return JSON.stringify(await tally.ledgers());
      case "get_ledger_balance":
        return JSON.stringify(await tally.ledger(String(args.name ?? "")));
      case "get_receivables":
        return JSON.stringify(await tally.receivables());
      case "get_payables":
        return JSON.stringify(await tally.payables());
      default:
        return JSON.stringify({ error: `unknown tool ${name}` });
    }
  } catch (e) {
    return JSON.stringify({ error: e instanceof Error ? e.message : String(e) });
  }
}
