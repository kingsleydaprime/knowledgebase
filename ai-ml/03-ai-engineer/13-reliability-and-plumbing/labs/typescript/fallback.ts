// fallback.ts — when one model fails, try the next one; when every model fails, degrade instead of erroring.

export type Option<T> = { name: string; run: () => Promise<T> };

/** A 400 or 422 means the request itself is wrong, so every model will reject it too. Don't hide that. */
const requestIsWrong = (error: unknown) => [400, 422].includes((error as { status?: number })?.status ?? 0);

export async function firstThatWorks<T>(
  options: Option<T>[],
  onFailure: (name: string, error: unknown) => void = () => {},
): Promise<{ by: string; value: T }> {
  const errors: unknown[] = [];
  for (const option of options) {
    try {
      return { by: option.name, value: await option.run() };
    } catch (error) {
      if (requestIsWrong(error)) throw error;
      onFailure(option.name, error); // log it: a fallback that hides a dead primary for a month is its own outage
      errors.push(error);
    }
  }
  throw new AggregateError(errors, `all ${options.length} options failed`);
}
