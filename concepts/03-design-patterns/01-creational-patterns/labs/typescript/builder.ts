// builder.ts — a builder earns its place when build() can check the whole object
export type Email = { to: string[]; subject: string; text: string; cc: string[]; replyTo?: string };

export class EmailBuilder {
  #to: string[] = [];
  #cc: string[] = [];
  #subject = "";
  #text = "";
  #replyTo: string | undefined;

  to(address: string) { this.#to.push(address); return this; }
  cc(address: string) { this.#cc.push(address); return this; }
  subject(value: string) { this.#subject = value; return this; }
  text(value: string) { this.#text = value; return this; }
  replyTo(address: string) { this.#replyTo = address; return this; }

  build(): Email {
    if (this.#to.length === 0) throw new Error("an email needs at least one recipient");
    if (!this.#subject) throw new Error("an email needs a subject");
    const overlap = this.#cc.filter((a) => this.#to.includes(a));
    if (overlap.length) throw new Error(`in both to and cc: ${overlap.join(", ")}`);
    return { to: [...this.#to], cc: [...this.#cc], subject: this.#subject, text: this.#text, replyTo: this.#replyTo };
  }
}
