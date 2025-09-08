import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  documents: defineTable({
    fieldOne: v.string(),
    fieldTwo: v.object({
      subFieldOne: v.array(v.float64()),
    }),
  }),
});


