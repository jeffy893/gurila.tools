# Gurila.Tools

> No one tool is fit for all jobs.

These tools are helpful for tactics within the disciplines of **enterprise**, **marketing**, and **culture**.

---

## Frameworks

Frameworks help figure out the **who, what, where, when, why, How**; and, the level of detail to come in at when modeling views to transition from the **AS IS** to the **TO BE**.

* **La Distinción:** To set a framework for cultural capital.
* **Marketing:** To set a framework for marketing.
* **DoD Framework and Data Dictionary:** To pick what view should be used in a military context.
* **IAF (Integrated Architecture Framework):** To pick what view should be used in an enterprise context.
* **Zachman Framework:** To pick what view should be used in a general context.

---

## [Account Ninja](./account.ninja/) 🥷

Account Ninja is a simple, client-side browser application designed to help you manage a list of financial accounts or goals. It allows you to prioritize these accounts, assign them a "3Zen" weight ([how much sense they make](./CapitalScopeSocial.pdf)), and track urgency by days remaining. You can then distribute a lump sum of money across these accounts based on these factors.

### How to Run

1.  **Download Files:** Make sure you have `index.html`, `style.css`, and `script.js` in the same folder on your computer. (These files would be generated separately as per the previous request).
2.  **Open in Browser:** Open the `index.html` file directly in your web browser (e.g., Chrome, Firefox, Edge, Safari). No web server or special tools (like Node.js) are required.

### Features

* **Add Accounts:** Add new financial goals or accounts with:
    * Account Name
    * Goal Amount ($)
    * Priority (1 being the highest, lower numbers are higher priority)
    * 3Zen Weight (a float number between 1 and 3, representing importance or "sense")
    * Days Remaining (urgency factor)
* **Display List:** View all your accounts in a table showing:
    * Account Name
    * Goal Amount
    * Current Amount (editable directly in the table)
    * Remaining Amount to Reach Goal
    * Priority (editable)
    * 3Zen Weight (editable)
    * Days Remaining (editable)
* **Edit In-Place:** Modify the `Current Amount`, `Priority`, `3Zen Weight`, and `Days Remaining` for any account directly in the table. Changes are saved automatically.
* **Delete Accounts:** Remove accounts from your list.
* **Distribute Funds:**
    * Enter a total amount of money you wish to distribute.
    * Click "Distribute." The application will allocate this money across your accounts.
    * The distribution logic considers:
        1.  **Need:** Only accounts where `Current Amount` < `Goal Amount` are eligible.
        2.  **Priority:** Lower priority numbers get higher preference.
        3.  **3Zen Weight:** Higher 3Zen weights get more preference.
        4.  **Urgency (Days Remaining):** Fewer days remaining (higher urgency) get more preference.
        *The formula for an account's weight in the distribution is roughly `(3Zen Weight * Urgency) / Priority`.*
        *Funds are distributed proportionally based on these calculated weights. The process may iterate to distribute any remainder if accounts reach their goal during allocation.*
* **Data Persistence:** Your account list and current amounts are saved in your browser's **`localStorage`**. This means the data persists between sessions *on the same browser and computer*.

### Calculation Logic for Distribution

When you click "Distribute":
1.  The app identifies accounts that still need funding (Goal > Current).
2.  For each eligible account, a `calculatedWeight` is determined:
    ```
    calculatedWeight = (3ZenWeight * (1 / (daysRemaining + 0.001))) / priority
    ```
    *(A small epsilon, 0.001, is added to daysRemaining to prevent division by zero and ensure 0 days has the highest urgency).*
3.  The total amount to distribute is then divided among eligible accounts based on the proportion of their `calculatedWeight` relative to the sum of all `calculatedWeight`s.
4.  An account will not receive more than its `goalAmount - currentAmount`.
5.  The distribution process may run in passes to attempt to allocate the full distribution amount if initial allocations fill up some accounts, freeing up funds for others still in need.

### Important Limitations

* **No True SQLite Database:** This app uses `localStorage`, which is built into your web browser.
    * Data is stored **locally** in your browser. It is not a separate `.sqlite` file that you can easily move or access with other database tools.
    * If you clear your browser's cache/data, or use a different browser or computer, your Account Ninja data will not be there.
* **Client-Side Only:** All logic (calculations, data storage) happens within your web browser. There is no backend server.
* **Manual Priority Management:** You are responsible for setting and managing the `Priority` numbers. The application uses these numbers as provided; it does not automatically re-sequence them if an item is deleted or if numbers are not unique/sequential (though non-unique priorities will simply share the same priority level in calculations).
* **Error Handling:** Basic validation is in place, but it's a simple app, not a robust commercial product.

Enjoy managing your accounts like a Ninja! 🥷💰

---

## Posterity App

This app begins **resource allocation simulation** and **models of conflict**.

Posterity is an Android App that simulates the Mating Dances of Bison and Cattle.
* To dance with **potency** is to dance like Bison.
* To take the **path of least resistance** is to dance like Cattle.

A Markov Chain incrementally "hands off" bounded constants to a Guerrilla Lanchester Law.

> The attrition factors are set in a way such that Bison are distinct from Cattle - differentiated by their Mating Dance.

* The **Heat Slider** is meant to represent the relative likelihood of a dance.
* The **Pace Slider** could be thought of as the relative pace of the dance floor.

The graph that appears after the simulation takes place is based on artificial criteria for:

* **Should the optimum size of each side of the dance be 3, 7, or 12?**
    * Indicated by the Y Axis.
* **Will Bison or Cattle win the conflict within 1.5 hours?**
    * Indicated by the X Axis.
* **Will there be a cross-over between Bison and Cattle?**
    * Ideal for those aiming to experience an event with longevity and balance.

<img src="https://user-images.githubusercontent.com/54923460/150920476-260fc2cd-37d7-43ba-8bdb-11eb921fe180.PNG"
     width="300" 
     height="700" />
<img src="https://user-images.githubusercontent.com/54923460/150920472-28c8ebf7-0419-416d-8b17-9b8f95e53c4f.PNG"
     width="300" 
     height="700" />
<img src="https://user-images.githubusercontent.com/54923460/150920477-0e738f5e-8884-4536-8185-3fd7be8e32d0.PNG"
     width="300" 
     height="700" />
<img src="https://user-images.githubusercontent.com/54923460/150920479-61b5e18b-96dc-430b-9e98-0a4f64050012.PNG"
     width="300" 
     height="700" />
<img src="https://user-images.githubusercontent.com/54923460/150920482-577c7cf5-7c11-4bfe-ad30-c77db4473e89.PNG"
     width="300" 
     height="700" />

---   

## Anomaly Detection

> An [event store](https://www.cortext.io/how-it-works) service is needed to queue the anomalies, asynchronously.

* **Pattern Deviation:** Anomalies are based on the pattern from which the anomaly veers.
* **Stakeholder Impact (The "So What?"):** Forward-filling the stakeholders is helpful to think about this.
* **Workflow Replication:** Backfill the workflow that could be used to catch the anomaly again.
* **Conflict Risk:** Synchronizing discussion about the anomalies detected carries the risk of conflict, which can lower morale.

---

## Dream Tactics

> This is like flossing the subconscious so that deep cleanings are not required.

* **Metadata:** Filled out last.
* **Approach:** The initial glimpse.
* **Formation:** Bullet points laying out the key points of the dream.
* **Execution:** Stream of consciousness, ultimately leading to the "So What?".

---

## MANGO Diplomacy

> **M**aeutic and **A**pplicable **N**egotiations, **G**uarantees, and **O**pportunities will arise, and you need to write them down.

* **PACBULOC:**
    * **P**arties
    * **A**ssumptions
    * **C**onditions
    * **B**oundaries
    * **U**ncertainties
    * **L**iabilities
    * **O**bjectives
    * **(Opportunity) C**osts

---

## Posterity Clarify

Queueing up ideas that may be shared helps to set a filter for what ultimately gets published.

---

## Lanchester Law Solution

This can be used with numerical methods in a computer to simulate conflict.

---

## Constitution of MANGO

These are some critical duties which set limitations on communications and behavior for MANGO Diplomacy.

---

## Phone Deprivation

This is a solution to a hyperbolic partial differential equation, intended to kick off the mathematics needed to prove the integration of phones into our nervous systems. This could implicate Medical Malpractice Precedence, so that idiosyncrasy credit may replace the bleed from TRIA (Terrorism Risk Insurance Act).

---

## Celestial Clockwork

This is a symbolic integration of "3sens" capital into the Lanchester Law.

---

## Intention div Negligence

This reverses the determination of negligence and indicates that intention should not be determined unless the individual has duties and agreements they are bound by.

---

## Morale Model of War and Love

This will be integrated with the Lanchester Law as one of the processes that hands off incremental values to the scope/social constant(s).

---

## Resource Allocation Simulation

> This runs through the simulations available with MATLAB and indicates a Gantt chart is a useful daily tool. The focus, however, should be on what *cannot* fit in the Gantt.

---

## Fraud Detection Bayonet

This is a thought experiment about fraud.

---

## Game: Re-Porter-Potty

This is a board game that sheds light on "potty reporters."

---

## Clusteral Solidarity Hedge

This models dignity and esteem in the context of micro-hegemony.

---

## Gurila Skej

This is a daily scheduler. **PACBULOC** (from MANGO Diplomacy) may be used in the time-block section for noting the MANGOs.

---

## Year-Gurila-Scheduler

This is a monthly scheduler.

---

## CapitalScopeSocial

This is "3Zen" accounting.