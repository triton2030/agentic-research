export async function POST(req: Request) {
  const { accountId } = await req.json();
  // TODO: rebuild the report for accountId
  return Response.json({ ok: true, accountId });
}
