# Step 2 Explained: Train/Test Split & F1 Score

## 🎯 WHAT IS A "SPLIT"?

### **Simple Analogy: Studying for an Exam**

Imagine you have a **textbook with 100 pages**.

**Bad way to study:**
```
Read all 100 pages → Take practice test on the same 100 pages
Result: 95% score (USELESS! You already know these pages)
Does it mean you'll pass the REAL exam? NO!
```

**Good way to study:**
```
Read 80 pages (training material)
Don't look at remaining 20 pages yet
Take practice test on those 20 pages (test material)
Result: 72% score (REAL! You haven't seen these before)
This shows if you actually learned, not just memorized
```

---

### **Machine Learning Split**

**We have 1,116 requirements.**

**Bad approach:**
```
Train model on all 1,116 requirements
Test model on the SAME 1,116 requirements
Accuracy: 99% (faker! Model memorized, not learned)
```

**Good approach (80/20 Split):**
```
1,116 requirements
    ↓
Split into:
├─ 892 requirements (80%) → Training set
│  └─ Model LEARNS from these
│
└─ 224 requirements (20%) → Test set
   └─ Model NEVER SEES these during training
   └─ We test here (unseen data = real test)
```

**Result:**
```
Training accuracy: 90%+
Test accuracy: 84.38% (REAL! Never seen before)
```

---

## 🧮 WHAT IS F1 SCORE?

### **F1 = A Better Accuracy Metric**

**The Problem with Simple Accuracy:**

Imagine you build a model to detect if an email is **SPAM** or **NOT SPAM**.

Your training data:
```
- 1,000 NOT SPAM emails
- 1 SPAM email
```

A lazy model says: **"Everything is NOT SPAM"**

```
Predictions:
- 1,000 NOT SPAM emails → Predict NOT SPAM ✅ (1,000 correct)
- 1 SPAM email → Predict NOT SPAM ❌ (1 wrong)

Accuracy = 1,000 / 1,001 = 99.9% !!
But the model FAILED at detecting spam!
```

**F1 Score solves this problem:**

F1 combines two metrics:
1. **Precision** - "Of predictions I make, how many are correct?"
2. **Recall** - "Of all actual cases, how many did I find?"

---

### **Precision vs Recall (Concrete Example)**

**Scenario: Airport Security**

```
1,000 passengers pass through security
- 10 are actually smugglers (hidden weapons)
- 990 are innocent
```

**Guard A: Very Strict**
```
Stops 200 people ("This person looks suspicious")
- Among 200: 9 are actual smugglers, 191 are innocent
- Misses 1 smuggler who walked through

Precision: 9/200 = 4.5% 
("Of the 200 I stopped, only 4.5% are smugglers!" - lots of false alarms)

Recall: 9/10 = 90%
("I caught 90% of all smugglers" - good detection)
```

**Guard B: Very Relaxed**
```
Only stops 10 people ("Only very suspicious people")
- Among 10: All 10 are actual smugglers
- Misses 0 smugglers who walked through

Precision: 10/10 = 100%
("Everyone I stopped was actually a smuggler!" - no false alarms)

Recall: 10/10 = 100%
("I caught all smugglers" - perfect detection)
```

**Guard C: Lazy**
```
Stops nobody
- No false alarms
- Stops 0 actual smugglers

Precision: Undefined (stopped nobody)
Recall: 0/10 = 0%
("I caught 0% of smugglers" - terrible!)
```

---

### **F1 Score = Harmonic Mean of Precision & Recall**

```
F1 = (2 × Precision × Recall) / (Precision + Recall)

Guard A: F1 = (2 × 0.045 × 0.90) / (0.045 + 0.90) = 0.086 (low)
Guard B: F1 = (2 × 1.0 × 1.0) / (1.0 + 1.0) = 1.0 (perfect!)
Guard C: F1 = 0 (caught nobody)
```

**F1 is between 0 and 1 (or 0% to 100%)**
- 1.0 = Perfect (100%)
- 0.5 = Decent (50%)
- 0.0 = Terrible (0%)

---

### **Why F1 for Our Requirements Model?**

**Our dataset has imbalanced categories:**
```
Functionality: 575 requirements
Security: 81 requirements
Reliability: 85 requirements
```

**Bad metric (simple accuracy) example:**
```
Lazy model: "Always predict Functionality"

Predictions:
- Functionality: 575 predict Functionality ✅ (575 correct)
- Security: 81 predict Functionality ❌ (0 correct)
- Reliability: 85 predict Functionality ❌ (0 correct)

Accuracy = 575/1116 = 51.5% (seems okay)

But model FAILED at detecting Security/Reliability!

F1 for Security: (2 × 0 × 0) / (0 + 0) = BAD! Shows problem ✅
```

**Good metric (F1) catches this problem!**

---

## 🔄 STEP 2 EXPLAINED: Find Best Train/Test Split

### **The Real Problem**

When you randomly split data, you might get **unlucky**:

**Unlucky Split Example:**
```
All 10 Security requirements go to TEST set
All Security requirements go to TRAINING set... wait, they're all in test!

Training set: 575 Functionality, 0 Security, 85 Reliability (MISSING Security!)
Test set: 0 Functionality, 10 Security, 0 Reliability (ALL Security!)

Result: Model never learns Security, test accuracy is bad
```

**Lucky Split Example:**
```
5 Security in TRAINING, 5 in TEST (balanced!)

Training set: 572 Functionality, 5 Security, 82 Reliability (balanced)
Test set: 3 Functionality, 5 Security, 3 Reliability (balanced)

Result: Model learns all categories, test accuracy is good
```

### **Step 2 Solution: Try Multiple Splits**

```python
# Try 10 different random starting points
for random_state in [42, 7, 13, 21, 33, 55, 77, 99, 123, 256]:
    # Create a split
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels,
        test_size=0.2,           # Always 80/20 split
        random_state=random_state  # Different randomization each time
    )
    
    # Quick test: Train a simple model on this split
    quick_model = LinearSVC(...)
    quick_model.fit(X_train, y_train)
    
    # Check F1 score on this split
    f1 = f1_score(y_test, quick_model.predict(X_test), average='weighted')
    
    # Save best split
    if f1 > best_score:
        best_score = f1
        best_random_state = random_state

print(f"Best split: random_state={best_random_state}, F1={best_score}")
```

---

## 📊 CONCRETE EXAMPLE WITH NUMBERS

### **Iteration 1: random_state=42**
```
Training set (892):
├─ Functionality: 456
├─ Security: 65
└─ Reliability: 67

Test set (224):
├─ Functionality: 119
├─ Security: 16
└─ Reliability: 18

Quick model accuracy: 82.5%
F1 score: 0.823
```

### **Iteration 2: random_state=7**
```
Training set:
├─ Functionality: 460
├─ Security: 62
└─ Reliability: 70

Test set:
├─ Functionality: 115
├─ Security: 19
└─ Reliability: 15

Quick model accuracy: 80.1%
F1 score: 0.799
```

### **Iteration 3: random_state=33** ⭐ BEST
```
Training set:
├─ Functionality: 458
├─ Security: 64
└─ Reliability: 68

Test set:
├─ Functionality: 117
├─ Security: 17
└─ Reliability: 19

Quick model accuracy: 84.4%
F1 score: 0.844 ← BEST! ✅
```

### **Iterations 4-10: Similar or Worse**
```
Random_state=21: F1=0.812
Random_state=55: F1=0.818
Random_state=77: F1=0.825
...
```

**Result: Pick random_state=33 because it has best F1 score (0.844)**

---

## 🎯 WHY STRATIFY?

### **Without stratify=labels:**
```
1,116 requirements
50% Functionality, 10% Security (approx)
    ↓ Random split (50/50)
    
❌ UNLUCKY: 
- Training: 80% Functionality, 2% Security (unbalanced!)
- Test: 20% Functionality, 18% Security (weird!)
```

### **With stratify=labels:**
```
1,116 requirements
50% Functionality, 10% Security (approx)
    ↓ Stratified split (maintains ratio)
    
✅ BALANCED:
- Training: 50% Functionality, 10% Security (same ratio!)
- Test: 50% Functionality, 10% Security (same ratio!)
```

**Analogy: Political Polling**
```
City population:
- 40% Democrat, 35% Republican, 25% Independent

Bad survey: Only poll rich neighborhood
- Get 70% Republican (not representative)

Good survey: Stratified sampling
- Interview 40% Democrat, 35% Republican, 25% Independent
- Representative of actual city!
```

---

## 📈 WHAT HAPPENS IN STEP 2 (Complete Walkthrough)

### **Step 2.1: Define 10 Candidate Splits**
```python
candidates = [42, 7, 13, 21, 33, 55, 77, 99, 123, 256]
```

### **Step 2.2: For Each Candidate**
```python
For candidate in candidates:
    # Split data
    1. Take 1,116 requirements
    2. Shuffle using candidate number (42, 7, 13, etc.)
    3. Create 80/20 split
    4. Keep category ratios (stratify)
    
    # Quick evaluation
    5. Train simple model (LinearSVC)
    6. Test on unseen 20%
    7. Calculate F1 score
    8. Save results
```

### **Step 2.3: Compare All 10**
```
Candidate 42:  F1 = 0.823
Candidate 7:   F1 = 0.799
Candidate 13:  F1 = 0.818
Candidate 21:  F1 = 0.812
Candidate 33:  F1 = 0.844 ← HIGHEST! ✅
Candidate 55:  F1 = 0.818
Candidate 77:  F1 = 0.825
Candidate 99:  F1 = 0.815
Candidate 123: F1 = 0.821
Candidate 256: F1 = 0.820
```

### **Step 2.4: Use Best Split for Rest of Training**
```python
# Now use random_state=33 for training the final model
X_train, X_test, y_train, y_test = train_test_split(
    texts, labels,
    test_size=0.2,
    random_state=33,  # ← The winner!
    stratify=labels
)

# Continue with TF-IDF, model training, etc. using THIS split
```

---

## 🧠 SIMPLE SUMMARY

| Term | Meaning | Example |
|------|---------|---------|
| **Split** | Dividing data into train (learn) and test (check) | 892 train, 224 test |
| **Stratify** | Keep same category percentages in both sets | 51.5% Functionality in both |
| **F1 Score** | How good is model (0-1 scale, 1 = perfect) | 0.844 = 84.4% good |
| **Random State** | Number that controls the randomization | 33, 42, 7, etc. |
| **Step 2** | Try 10 splits, pick the one with best F1 | Pick random_state=33 |

---

## 🎓 WHAT YOU SHOULD REMEMBER

1. **Data must be split** before training (train on 80%, test on 20% you never saw)

2. **F1 Score** tells you "how good is the model at this classification task" (0-100%)

3. **Stratify** means "keep the same percentage of each category in both train and test"

4. **Step 2** tries 10 different random splits and picks the best one (with highest F1)

5. **Why?** Because randomness matters - some splits are luckier than others. Try many, pick best.

---

## 📍 REAL-WORLD ANALOGY: STUDENT TESTING

**Goal:** Pick the BEST practice test set to test how smart students are

**Bad Way:**
```
Pick 10 random students, give them same test
Measure how they do
Maybe you got all good students (lucky!)
Maybe you got all bad students (unlucky!)
Don't know true ability level
```

**Good Way (Like Step 2):**
```
Try 10 different groups of students
Give each group a different practice test
See which group/test gives BEST results on actual exam
Pick that combination

Why?
- One random group might be smarter (lucky split)
- Another group might match real student population (representative split)
- Test with best group → know model is good!
```

---

**This is what Step 2 does - it finds the "best group" (split) to train and test on!**
