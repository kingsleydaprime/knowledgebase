import { db } from "@/shared/db";
import { formatKobo } from "../shared/money";
import { findUser } from "../users";
import { charge } from "../payments";
import express from "express"; // a package, not a module of ours: ignored
export const markPaid = (id: string) => db.rows.push(id);
export const checkout = (userId: string, id: string) => [findUser(userId), charge(id), formatKobo(500), express];
