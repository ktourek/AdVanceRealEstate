# Questions for Tobi (ERD Designer)

Hi Tobi,

I have two questions regarding the database schema design:

---

## 1. Photo Table - Column Name Spelling

**Question:** In the Photo table, the ERD shows the column name as `Phot_Display_Order` (missing the 'o' in Photo). 

**Current ERD:** `Phot_Display_Order`  
**Implementation:** `Photo_Display_Order` (corrected spelling)

**Question:** Should this be `Photo_Display_Order` (with the 'o') instead of `Phot_Display_Order`? We've implemented it as `Photo_Display_Order` since that seems like the correct spelling, but wanted to confirm with you before finalizing.

---

## 2. User Table - Username Column

**Question:** In the User table, we currently have:
- `User_ID` (PRIMARY KEY)
- `Email` (TEXT NOT NULL)
- `Password_Hash` (TEXT NOT NULL)
- `Firstname` (TEXT NOT NULL)
- `Lastname` (TEXT NOT NULL)

**Question:** Do we need a separate `Username` column, or can we use `Email` as the username for authentication purposes?

**Context:** 
- Currently, our implementation uses `Email` as the unique identifier for user authentication (no separate username field)
- This matches the ERD schema exactly, but we want to confirm this is the intended design
- If a separate username is needed, we'll need to add it to the schema

**Thoughts?** Should we add a `Username` column, or is using `Email` as the username acceptable?

---

Thanks!  
[Your Name]

