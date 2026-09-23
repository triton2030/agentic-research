// Расписание фоновых задач.
export function nextRuns(expr, count) {
  const now = new Date();
  return Array.from({ length: count }, (_, i) => new Date(now.getTime() + (i + 1) * 15 * 60 * 1000));
}
