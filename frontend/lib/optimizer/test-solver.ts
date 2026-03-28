import { solveLP } from './solveLP';

const testInput = {
  foods: [
    {
      id: 1,
      name: "Expensive Chicken",
      cost_per_100g: 5.0,
      calories_per_100g: 165,
      protein_per_100g: 30,
      carbohydrate_per_100g: 0,
      fat_per_100g: 3,
      fiber_per_100g: 0,
      created_at: "2026-03-28T10:00:00Z",
      updated_at: "2026-03-28T10:00:00Z"
    },
    {
      id: 2,
      name: "Cheap Whey",
      cost_per_100g: 1.0,
      calories_per_100g: 120,
      protein_per_100g: 25,
      carbohydrate_per_100g: 2,
      fat_per_100g: 1,
      fiber_per_100g: 0,
      created_at: "2026-03-28T10:00:00Z",
      updated_at: "2026-03-28T10:00:00Z"
    }
  ],
  objective: 'min_cost' as const,
  targetValue: 0,
  constraints: [
    { id: 'c1', category: 'protein' as const, operator: '>=' as const, value: 100 }
  ],
  bounds: {}
};

const result = solveLP(testInput);
console.log(JSON.stringify(result, null, 2));
