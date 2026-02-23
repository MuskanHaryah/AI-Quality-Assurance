# Visual Guide: Split, F1 Score, and Step 2

## 1️⃣ WHAT IS A SPLIT? (Visual)

### **Before Split:**
```
📚 1,116 Requirements (Mixed)
├─ Functionality ①②③④⑤...
├─ Security ⓐⓑⓒⓓ...
├─ Reliability ◆◆◆◆...
└─ Other categories...
```

### **After 80/20 Split:**
```
TRAINING SET (80%)          TEST SET (20%)
┌─────────────────────┐    ┌──────────────┐
│ 892 Requirements    │    │ 224 Reqs     │
│                     │    │              │
│ ①②③④⑤... (Func)   │    │ ⑥⑦⑧ (Func) │
│ ⓐⓑⓒ (Security)     │    │ ⓓⓔ (Sec)   │
│ ◆◆◆◆ (Reliab)     │    │ ◆◆ (Rel)   │
│ ... others          │    │ ...          │
│                     │    │              │
│ ✓ Model LEARNS     │    │ ✗ Never seen │
│   (Sees these)      │    │   before     │
│                     │    │   (Hidden   │
│                     │    │    test)    │
└─────────────────────┘    └──────────────┘
```

**Rule:** Model trains on LEFT, gets tested on RIGHT (which it never saw)

---

## 2️⃣ WHAT IS F1 SCORE? (Visual)

### **Metric Comparison:**

```
                    🎯 ACCURACY (Simple)
                    ├─ "Out of 100 tests, how many did you pass?"
                    └─ Problem: Ignores if some tests are harder
                    
                    🎯 PRECISION  (Part of F1)
                    ├─ "When you say YES, how often are you RIGHT?"
                    └─ Example: 90% of your positive predictions correct
                    
                    🎯 RECALL     (Part of F1)
                    ├─ "Out of all positives, how many did you FIND?"
                    └─ Example: You found 85% of all true positives
                    
                    🎯 F1 SCORE   (Best for imbalanced data)
                    ├─ Combines Precision & Recall
                    ├─ 0.0 = Terrible ❌
                    ├─ 0.5 = Okay ⚠️
                    └─ 1.0 = Perfect ✅
```

### **F1 Score Range:**
```
0.0 ───────────────────────────────────────── 1.0
 ❌ Bad      ⚠️ Okay        ✅ Good      ⭐ Perfect
Terrible   Not great    Pretty good    Excellent

Our model: 0.844 = 84.4% (Good!)
```

### **Real Example: Email Spam Detection**
```
Your spam filter makes these predictions:

100 spam predictions
├─ 95 are actually spam ✅
└─ 5 are innocent emails ❌ (false alarm)

PRECISION = 95/100 = 95%
"When I say spam, I'm 95% right"

1000 actual spam emails in inbox
├─ 900 got caught by filter
└─ 100 slipped through to inbox

RECALL = 900/1000 = 90%
"I catch 90% of all spam"

F1 = (2 × 0.95 × 0.90) / (0.95 + 0.90) = 0.924
F1 = 92.4% ✅ Very good!
```

---

## 3️⃣ STEP 2: Find Best Split (Visual Walkthrough)

### **The Problem (Why Step 2 Exists):**

```
❌ BAD: Random split might be unlucky
┌──────────────────────────────────────────┐
│ Tried random_state=7                      │
│                                           │
│ Training set: Mostly Functionality       │
│               (Model learns only Func)   │
│                                           │
│ Test set: Mostly Security                │
│           (Model tested on unknown)      │
│                                           │
│ Result: Model fails! ❌                  │
└──────────────────────────────────────────┘

⭐ GOOD: Find the lucky split
┌──────────────────────────────────────────┐
│ Tried random_state=33                     │
│                                           │
│ Training set: All categories balanced    │
│               (Model learns everything)  │
│                                           │
│ Test set: All categories balanced        │
│           (Fair test)                    │
│                                           │
│ Result: Model succeeds! ✅               │
└──────────────────────────────────────────┘
```

### **Step 2 Process (Simplified):**

```
STEP 1: Create 10 candidate splits
┌─────────────────────────────────────────────────────────────┐
│ random_state=42
│ random_state=7
│ random_state=13
│ random_state=21
│ random_state=33     ← Will be best ⭐
│ random_state=55
│ random_state=77
│ random_state=99
│ random_state=123
│ random_state=256
└─────────────────────────────────────────────────────────────┘

STEP 2: For each candidate, do a quick test
┌─────────────────────────────────────────────────────────────┐
│ For random_state=42:
│   → Split data (892 train, 224 test)
│   → Train quick model (LinearSVC)
│   → Test model
│   → Calculate F1 score = 0.823
│   → Save score
│
│ For random_state=7:
│   → Split data (892 train, 224 test)
│   → Train quick model (LinearSVC)
│   → Test model
│   → Calculate F1 score = 0.799
│   → Save score
│
│ ... repeat for all 10 ...
│
│ For random_state=33:
│   → Split data (892 train, 224 test)
│   → Train quick model (LinearSVC)
│   → Test model
│   → Calculate F1 score = 0.844 ← HIGHEST!
│   → Save score (THIS IS BEST!)
└─────────────────────────────────────────────────────────────┘

STEP 3: Compare all F1 scores and pick winner
┌─────────────────────────────────────────────────────────────┐
│ Results:
│  #1  random_state=33:  F1 = 0.844 ⭐ WINNER
│  #2  random_state=77:  F1 = 0.825
│  #3  random_state=42:  F1 = 0.823
│  #4  random_state=123: F1 = 0.821
│  #5  random_state=55:  F1 = 0.818
│  #6  random_state=13:  F1 = 0.818
│  #7  random_state=21:  F1 = 0.812
│  #8  random_state=99:  F1 = 0.815
│  #9  random_state=256: F1 = 0.820
│  #10 random_state=7:   F1 = 0.799
│
│ BEST: random_state=33 (F1=0.844)
└─────────────────────────────────────────────────────────────┘

STEP 4: Use the winning split for actual training
┌─────────────────────────────────────────────────────────────┐
│ Now use random_state=33 to create final split
│ → Train on 892 with this split
│ → Test on 224 with this split
│ → This is the lucky split that works best!
└─────────────────────────────────────────────────────────────┘
```

---

## 4️⃣ WHY STRATIFY? (Visual)

### **Without Stratify:**
```
Original data:
┌────────────────────────────────────────┐
│ 575 Functionality (51%)                │
│ 125 Usability (11%)                    │
│ 95 Efficiency (9%)                     │
│ 85 Reliability (8%)                    │
│ 81 Security (7%)                       │
│ 79 Maintainability (7%)                │
│ 76 Portability (7%)                    │
│ TOTAL: 1,116                           │
└────────────────────────────────────────┘

❌ Random split (unlucky)
┌──────────────────────────┐  ┌─────────────────┐
│ TRAINING (892)           │  │ TEST (224)      │
├──────────────────────────┤  ├─────────────────┤
│ Functionality: 520 (58%) │  │ Func: 55 (25%)  │
│ Usability: 110 (12%)     │  │ Usab: 15 (7%)   │
│ Efficiency: 88 (10%)     │  │ Effi: 7 (3%)    │
│ Others: 174 (20%)        │  │ Others: 147 (66%)
├──────────────────────────┤  ├─────────────────┤
│ ⚠️ IMBALANCED!           │  │ ⚠️ IMBALANCED!  │
└──────────────────────────┘  └─────────────────┘
```

### **With Stratify:**
```
✅ Stratified split (keeps same %)
┌──────────────────────────┐  ┌─────────────────┐
│ TRAINING (892)           │  │ TEST (224)      │
├──────────────────────────┤  ├─────────────────┤
│ Functionality: 456 (51%) │  │ Func: 119 (53%) │
│ Usability: 99 (11%)      │  │ Usab: 26 (12%)  │
│ Efficiency: 80 (9%)      │  │ Effi: 15 (7%)   │
│ Reliability: 76 (8%)     │  │ Reli: 9 (4%)    │
│ Security: 72 (7%)        │  │ Secu: 9 (4%)    │
│ Maintainability: 64 (7%) │  │ Main: 21 (9%)   │
│ Portability: 45 (5%)     │  │ Port: 25 (11%)  │
├──────────────────────────┤  ├─────────────────┤
│ ✅ BALANCED!             │  │ ✅ BALANCED!    │
└──────────────────────────┘  └─────────────────┘

Both sets have SAME distribution as original! ✅
```

---

## 5️⃣ COMPLETE STEP 2 FLOW (One Diagram)

```
START
  ↓
Have: 1,116 labeled requirements
  ↓
Create 10 candidate random states
  ├─ 42, 7, 13, 21, 33, 55, 77, 99, 123, 256
  ↓
FOR EACH candidate:
  ├─ Split: 892 train, 224 test (stratified)
  ├─ Train: Quick LinearSVC model
  ├─ Test: On 224 unseen requirements
  ├─ Measure: F1 score
  └─ Save: F1 result
  ↓
COMPARE all 10 F1 scores
  ├─ #1: 0.844 ← BEST (random_state=33)
  ├─ #2: 0.825
  ├─ #3: 0.823
  └─ ... 7 more ...
  ↓
SELECT: random_state=33 (highest F1)
  ↓
USE THIS SPLIT for actual model training
  ├─ Train 10 models (Logistic Regression, SVM, etc.)
  ├─ Each uses this lucky split
  ├─ Evaluate each model
  └─ Pick best model
  ↓
RESULT: Best model trained on best split ✅
```

---

## 6️⃣ ANALOGY: Movie Auditions

```
You're casting a movie. Need to pick best actor.

❌ BAD WAY:
- Hold audition on Monday
- Get 5 lucky actors who are having great day
- Pick "best" actor
- But Saturday's 5 actors would have been better!
- Result: Might pick wrong actor (unlucky split)

✅ GOOD WAY (Like Step 2):
- Hold auditions Monday-Friday (5 audition days)
- Rate each day's actors (F1 scores)
  - Monday: Average score 7/10
  - Tuesday: Average score 8/10  ← BEST DAY
  - Wednesday: Average score 6/10
  - Thursday: Average score 7/10
  - Friday: Average score 7.5/10
- Use Tuesday's audition format for final casting
- Pick best actor from best day's setup
- Result: Get the truly best actor ✅
```

---

## 📋 QUICK REFERENCE TABLE

| Concept | What | Why | Example |
|---------|------|-----|---------|
| **Split** | Divide data into train (learn) & test (check) | Model can't be tested on data it learned from | 892 train, 224 test |
| **Stratify** | Keep same proportions in both sets | Ensures fair representation | 51% Func in both |
| **F1 Score** | Metric combining Precision & Recall | Better than accuracy for imbalanced data | 0.844 = Good! |
| **Random State** | Number controlling randomization | Reproducibility - same number = same split | 33 = Best split |
| **Step 2** | Find best split using F1 score | Some random splits are luckier | Try 10, pick best |

---

## 🎯 WHAT STEP 2 ACTUALLY DOES

```
Input:  1,116 requirements
        
Process: Try 10 random splits
         For each: (Train → Test → Measure F1)
         Pick highest F1
        
Output: random_state=33
        F1 score = 0.844
        Ready for real training!
```

---

## ✅ BOTTOM LINE

1. **Split** = Dividing data for fair testing
2. **F1 Score** = Quality metric (0-1 scale)
3. **Stratify** = Keeping proportion balanced
4. **Step 2** = Finding the best way to split data
5. **Why?** = Some random splits are better than others

**Think of it like:** Trying 10 different ways to shuffle a deck of cards, measuring which shuffle is most fair, then using that shuffle method for the card game.

---

That's it! Step 2 is really about finding the "lucky split" that makes training work best. 🎲✅
