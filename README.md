# resonate-api

## Input
`i ate boiled rice with 200g chicken fillet`

## Parsed Foods and Matches
1. Chicken Fillet
   - Parsed: 
     ```json
     {
       "food": "chicken fillet",
       "quantity": 200,
       "unit": "g"
     }
     ```
   - Matched with: Chicken Breast (Score: 0.32)
     ```json
     {
       "food_id": "chicken-breast",
       "food_name": "Chicken Breast",
       "single_serving_size": 120.0,
       "quantity": 1.0,
       "quantity_unit": "breast",
       "calories": 198.0,
       "total_fat": 4.3,
       "total_carbohydrates": 0.0,
       "dietary_fiber": 0.0,
       "protein": 37.0
     }
     ```

2. Boiled Rice
   - Parsed:
     ```json
     {
       "food": "boiled rice",
       "quantity": 1,
       "unit": "cup"
     }
     ```
   - Matched with: Cooked Rice (Score: 0.23)
     ```json
     {
       "food_id": "cooked-rice",
       "food_name": "Cooked Rice",
       "single_serving_size": 158.0,
       "quantity": 1.0,
       "quantity_unit": "cup",
       "calories": 205.0,
       "total_fat": 0.4,
       "total_carbohydrates": 45.0,
       "dietary_fiber": 0.6,
       "protein": 4.3
     }
     ```