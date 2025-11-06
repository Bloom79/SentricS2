# SentricS2: Insanely Great Edition
## Experience Design Document

> "Design is not just what it looks like and feels like. Design is how it works." - Steve Jobs

---

## The Three-Second Experience

Every screen answers ONE question. Every action has ONE clear outcome. Every insight leads to ONE decision.

---

## 1. CER Billing: "Know Your Number Instantly"

### The Problem
Current UX: Upload CSV → Wait → View table → Calculate totals → Export report → Email members
**Time to insight: 4-6 hours**

### The Vision
Drag file → See your number → Understand what drives it
**Time to insight: 3 seconds**

### Screen 1: The Dashboard (Before Upload)

```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│                    YOUR CER EARNINGS                          │
│                                                               │
│                        €12,847                                │
│                   ↑ €1,203 (10.3%)                           │
│                   vs. last month                              │
│                                                               │
│            Last updated: Jan 15, 2025 10:32 AM                │
│                                                               │
│   ╔═══════════════════════════════════════════════════════╗  │
│   ║                                                       ║  │
│   ║    Drop your GSE or e-distribuzione file here        ║  │
│   ║                                                       ║  │
│   ║    We support all formats automatically              ║  │
│   ║                                                       ║  │
│   ╚═══════════════════════════════════════════════════════╝  │
│                                                               │
│                                                               │
│   📊 INSIGHTS THIS MONTH                                      │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ 🌞 Peak sharing: Weekdays 10am-2pm (avg €94/hour)   │   │
│   │ ⚠️  Low sharing: Weekends (avg €23/hour)            │   │
│   │ 💡 Opportunity: Add 50kWh storage → +€347/month     │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                               │
│                                                               │
│   📈 EARNINGS TREND (Last 6 Months)                           │
│   [Beautiful area chart showing growth]                       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Screen 2: The Magic Moment (During Upload)

```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│                 ✨ PROCESSING YOUR FILE                       │
│                                                               │
│                  consumptions_jan_2025.csv                    │
│                                                               │
│   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░ 87%                  │
│                                                               │
│   ✓ Detected format: GSE Portale SPC                         │
│   ✓ Found 720 hourly readings                                │
│   ✓ Matched 12 members by POD code                           │
│   → Calculating shared energy...                             │
│                                                               │
│                   1.2 seconds elapsed                         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Screen 3: The Insight (After Upload)

```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│                    YOUR CER EARNINGS                          │
│                                                               │
│                        €13,156                                │
│                   ↑ €1,512 (13.0%)                           │
│                   vs. last month                              │
│                                                               │
│                 🎉 NEW DATA PROCESSED                         │
│            January 2025 now complete (720 hours)              │
│                                                               │
│                                                               │
│   📊 WHAT CHANGED                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ January earnings: €13,156 (+€309 vs. estimate)      │   │
│   │                                                       │   │
│   │ Top performer: Giuseppe R. (€1,847 shared)          │   │
│   │ Biggest gain: Weekend solar (+18% vs. December)     │   │
│   │ Biggest loss: Industrial consumption (-8%)          │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                               │
│                                                               │
│   💡 INSTANT INSIGHTS                                         │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ • Peak sharing improved: Now 10am-3pm (was 11am-2pm)│   │
│   │ • Weekend performance up 18%                         │   │
│   │ • New opportunity: Shift EV charging to midday       │   │
│   │   → Potential +€124/month                            │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                               │
│   [Download Member Reports] [View Detailed Analytics]        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **The number is the hero** - €13,156 in giant type, front and center
2. **Progress is visible** - Green arrow, percentage, context
3. **Drag anywhere** - Drop zone isn't a small box, it's the ENTIRE screen on hover
4. **Instant feedback** - Processing shows what's happening in plain English
5. **Insights, not data** - Don't show 720 rows, show "Peak sharing: Weekdays 10am-2pm"

---

## 2. 15-Minute Trading: "Money on the Table"

### The Problem
Current UX: Check GME API → See prices → Manually calculate arbitrage → Decide curtailment
**Time to decision: 30-60 minutes daily**

### The Vision
Open app → See money you're leaving → Click to optimize
**Time to decision: 10 seconds**

### Screen 1: Morning Briefing

```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│                    🌅 GOOD MORNING                            │
│                   Thursday, Feb 6, 2025                       │
│                                                               │
│                                                               │
│              YOUR 6 PLANTS WILL MAKE                          │
│                                                               │
│                        €847                                   │
│                       today                                   │
│                                                               │
│                                                               │
│               BUT YOU COULD MAKE                              │
│                                                               │
│                       €1,203                                  │
│                                                               │
│                  +€356 (+42%)                                │
│                                                               │
│                                                               │
│   💰 HERE'S HOW TO GET IT                                     │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                                                       │   │
│   │  1. Curtail Plant #3 (Palermo) from 2:00-3:00pm     │   │
│   │     Price: -€12/MWh (you PAY to produce)            │   │
│   │     Savings: +€84                                    │   │
│   │                                                       │   │
│   │  2. Discharge BESS #1 at 7:00-8:00pm                │   │
│   │     Price: €180/MWh (peak demand)                    │   │
│   │     Revenue: +€144                                   │   │
│   │                                                       │   │
│   │  3. Shift BESS #2 charge to 1:00-2:00pm             │   │
│   │     Price: €15/MWh (solar surplus)                   │   │
│   │     Savings: +€128                                   │   │
│   │                                                       │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                               │
│                                                               │
│   [Apply All Optimizations] [Auto-Optimize Going Forward]    │
│                                                               │
│   [Show Me The Math] [Customize Preferences]                 │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Screen 2: Live Price Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│  15-MINUTE PRICES                                  LIVE      │
│  Sicily Zone (SICI)                           Feb 6, 2:47pm  │
│                                                               │
│   Current Quarter: 2:45pm-3:00pm                             │
│                                                               │
│                       -€8.40                                  │
│                      per MWh                                  │
│                                                               │
│                  ⚠️  NEGATIVE PRICE                           │
│                                                               │
│                                                               │
│   🎯 YOUR ACTION: CURTAIL PRODUCTION NOW                      │
│                                                               │
│   Plant #3 (Palermo) producing 280 kW                        │
│   You're PAYING €2.35 this quarter                           │
│                                                               │
│   [Curtail Now] [Ignore]                                     │
│                                                               │
│   ─────────────────────────────────────────────────────      │
│                                                               │
│   NEXT 8 QUARTERS (Next 2 Hours)                             │
│                                                               │
│   3:00pm   -€12  ⚠️  Still negative                          │
│   3:15pm    €3   ✓  Back to positive                         │
│   3:30pm   €15   ✓  Normal                                   │
│   3:45pm   €28   ✓  Rising                                   │
│   4:00pm   €45   ✓  Good                                     │
│   4:15pm   €67   ⭐ Strong                                    │
│   4:30pm   €89   ⭐ Peak building                             │
│   4:45pm  €124   🔥 PEAK - discharge BESS                    │
│                                                               │
│   [View Full Day] [Set Price Alerts]                         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Key Design Principles

1. **Money first** - "€847 today BUT could be €1,203"
2. **Clear actions** - Not "price is -€12", but "CURTAIL NOW, you're paying"
3. **Future visibility** - Next 8 quarters shown, not raw data
4. **One-click optimization** - "Apply All" button does the thinking
5. **Trust through transparency** - "Show Me The Math" explains every decision

---

## 3. BESS Monitoring: "Stop Losing Money"

### The Problem
Current UX: Check vendor app → View SOC → Check prices → Calculate optimal schedule → Manually adjust
**Time to optimization: Daily guesswork**

### The Vision
See performance score → Understand losses → Fix them
**Time to optimization: One click**

### Screen 1: Performance Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│              YOUR BESS PERFORMANCE SCORE                      │
│                                                               │
│                         87/100                                │
│                                                               │
│                    ⭐⭐⭐⭐☆                                    │
│                                                               │
│                   GOOD, BUT NOT GREAT                         │
│                                                               │
│                                                               │
│   💸 YOU'RE LOSING €15,284/YEAR                               │
│                                                               │
│   Here's exactly how to fix it:                              │
│                                                               │
│                                                               │
│   ⚠️  ISSUE #1: Missing Negative Price Opportunities         │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ Your BESS isn't charging during negative prices     │   │
│   │                                                       │   │
│   │ Last 30 days: 47 hours of negative prices           │   │
│   │ You missed: 2,115 kWh of "paid to charge" energy    │   │
│   │                                                       │   │
│   │ Annual loss: €8,400                                  │   │
│   │                                                       │   │
│   │ FIX: Enable auto-trading mode                        │   │
│   │ We'll charge when prices go negative automatically  │   │
│   │                                                       │   │
│   │ [Enable Auto-Trading] [Learn More]                  │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                               │
│                                                               │
│   ⚠️  ISSUE #2: Suboptimal Discharge Timing                  │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ You're discharging at average prices, not peaks     │   │
│   │                                                       │   │
│   │ Your avg discharge price: €67/MWh                    │   │
│   │ Optimal discharge price: €142/MWh                    │   │
│   │                                                       │   │
│   │ You're leaving €112/day on the table                │   │
│   │                                                       │   │
│   │ Annual loss: €4,900                                  │   │
│   │                                                       │   │
│   │ FIX: Shift discharge to 7-9pm peak window           │   │
│   │ We'll predict peaks and optimize timing              │   │
│   │                                                       │   │
│   │ [Optimize Discharge] [Show Price Forecast]          │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                               │
│                                                               │
│   ⚠️  ISSUE #3: Conservative Depth of Discharge              │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ You're only using 75% of battery capacity           │   │
│   │                                                       │   │
│   │ Your battery warranty allows 90% DOD                │   │
│   │ You're underutilizing 15% = 22.5 kWh/cycle          │   │
│   │                                                       │   │
│   │ Annual loss: €1,984                                  │   │
│   │                                                       │   │
│   │ FIX: Increase DOD to 90% (safe per warranty)        │   │
│   │ Adds 2,800 years to cycle life vs revenue gain      │   │
│   │                                                       │   │
│   │ [Increase DOD] [View Warranty Terms]                │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                               │
│                                                               │
│   [APPLY ALL FIXES → Save €15,284/year]                      │
│                                                               │
│   [Explain the Math] [Customize Settings]                    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Screen 2: Live Status (Sidebar Widget)

```
┌──────────────────────────────────┐
│                                  │
│  BESS #1 - Milan Depot           │
│                                  │
│  State of Charge                 │
│                                  │
│       ▓▓▓▓▓▓▓▓▓▓▓▓░░░░  78%     │
│                                  │
│  Status: CHARGING                │
│  Power: 45 kW                    │
│  Price: €12/MWh ✓ Good time     │
│                                  │
│  ────────────────────────────    │
│                                  │
│  Next Action:                    │
│  7:15pm - Discharge at peak      │
│  Expected revenue: €84           │
│                                  │
│  [View Details]                  │
│                                  │
└──────────────────────────────────┘
```

### Key Design Principles

1. **Score as shorthand** - 87/100 immediately communicates "good but fixable"
2. **Losses are concrete** - Not "suboptimal", but "€15,284/year"
3. **Fixes are specific** - Not "optimize", but "Enable auto-trading"
4. **One button to rule them all** - "Apply All Fixes" is the hero CTA
5. **Trust through detail** - Every number explained, every fix justified

---

## Design System Principles

### Typography
- **Hero numbers**: 72px, medium weight, tabular figures
- **Section headers**: 24px, semibold, tight tracking
- **Body text**: 16px, regular, comfortable line height (1.6)
- **Labels**: 14px, medium, uppercase, tracked

### Colors
```
Primary (Money Green):  #10B981
Danger (Loss Red):      #EF4444
Warning (Attention):    #F59E0B
Success (Gain):         #3B82F6
Neutral (Background):   #F9FAFB
Text (Primary):         #111827
Text (Secondary):       #6B7280
```

### Motion
- **Drag-drop**: Gentle scale (1.02x) + soft shadow on hover
- **Processing**: Smooth progress bar with micro-animations
- **Number changes**: Count-up animation over 800ms ease-out
- **Insights appear**: Slide-up + fade (400ms, stagger 100ms)

### Spacing
- Use 8px grid system
- Container max-width: 1280px
- Cards: 24px padding, 16px radius, subtle shadow
- Sections: 64px vertical spacing

---

## Technical Architecture

### Frontend Stack
- **Framework**: React 18 + TypeScript
- **Styling**: Tailwind CSS 3.x
- **Animation**: Framer Motion
- **State**: Zustand (lightweight, no boilerplate)
- **Charts**: Recharts (existing) + custom styling
- **File upload**: react-dropzone
- **Build**: Vite (fast, modern)

### Backend API Gateway
- **Framework**: FastAPI (thin layer)
- **Purpose**: Bridge new UI to existing backend services
- **Auth**: JWT passthrough from existing system
- **Endpoints**:
  - `/api/v2/cer/upload` → process CSV
  - `/api/v2/trading/briefing` → morning insights
  - `/api/v2/bess/performance` → score + losses

### Data Flow
```
New UI → API Gateway → Existing Backend Services → PostgreSQL
   ↓         ↓              ↓
 React    FastAPI     Your solid foundation
         (thin)       (unchanged)
```

---

## Success Metrics

### Quantitative
- **Time to insight**: 3 seconds (from 4-6 hours)
- **Decisions per day**: 3-5 one-click actions
- **User engagement**: Daily active usage >80%
- **Revenue optimization**: +15-30% captured opportunities

### Qualitative
- **User quote goal**: "It just works"
- **Support ticket reduction**: 70% (less confusion)
- **Feature requests**: Fewer "how do I..." questions
- **Emotional response**: Delight, not drudgery

---

## Next Steps

1. Build the frontend-v2 project
2. Implement CER Billing drag-drop magic
3. Create 15-Min Trading morning briefing
4. Build BESS performance dashboard
5. Wire up API gateway
6. Deploy side-by-side with existing UI
7. A/B test with 10 users
8. Iterate based on real usage

---

**Remember**: Features tell. Experiences sell.

**This is how we win the Italian energy market.**
