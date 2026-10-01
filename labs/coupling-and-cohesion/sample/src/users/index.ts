import { db } from "../shared/db";
export const findUser = (id: string) => ({ id, db });
