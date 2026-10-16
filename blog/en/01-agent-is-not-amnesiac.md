# Agents Aren't Amnesiac — They Can't Find the Entry Point: Documentation Layers for Large Projects (1)

*This post is an English translation of the Chinese original: [Agent 不是失忆，是找不到入口——大型项目文档分层设计（一）](../01-agent-is-not-amnesiac.md).*

> This is the first post in the series "Agent-first Documentation Layers for Large Projects." The material comes from seven months of AI-collaborative development on an enterprise payment-approval system: I wrote code, tests, and docs together with Claude Code, Codex, and Kimi. The series covers only the documentation leg. Test methodology is a separate topic.

## 1. Two release seals, and a spec that was already written

On September 16, an enterprise payment-approval system was tagged twice, two versions on the same day. Neither version had a changelog or a handover note at the time.

Two days later a commit landed that did three things at once: it added a standalone release-seal spec (release seal: freeze the version, run the full test suite, tag, and produce the package); it added an "operation → required reading" table to the entry file; and it backfilled the release documents those two versions had skipped — a changelog for business users and a handover note for operations. The introduction above the table wrote the lesson into the entry rules for the agent: "sealed a release without reading the full-suite definition, and skipped the release documents."

The definition of "full" was not new that day. **The spec already existed.** "The full run always includes the following six suites; none may be omitted" was already in the project testing spec. The docs home mentioned the "six-suite full-run discipline." The change plans for two earlier release seals had also required six-suite test evidence. The spec itself was enough. What was missing was the path from the entry file to it.

Look at the entry file before that rule was written — the Markdown file loaded automatically at the start of every session. It was 410 lines. On shipping a release, the only text was a tagging rule tucked inside the Git branch conventions. The words "full suite" and "release seal" never appeared. From the entry, nothing pointed a release seal at that testing spec.

The new release-seal spec spelled out the six-suite definition, the release-seal checklist, and the required contents of the two release documents. The first row of the table in the entry file looked like this (excerpt, redacted):

| Operation | Required reading |
|---|---|
| Release seal / produce a package / tag / say "full suite green" | Release-seal spec (six-suite definition + checklist + templates for the two release documents) |

Notice the last item in the first column: saying "full suite green." **Saying a sentence** was registered as an operation. Before the agent may utter those words, it has to read that spec. (The second column says "templates." The spec body actually tells the agent to imitate a historical document. That trap waits for post 3.) As of October 14, the nine versions from v2.0.5 through v2.3.1 after the rule was written each have both a changelog and a handover note. Post 2 goes into the detail.

So "the agent keeps forgetting things" blames the wrong object. The agent is not amnesiac. It never had memory across sessions. Every session is a newcomer walking in through the entry. The problem is that the entry does not take it where it needs to go. The series has one thesis: **in a project where an agent writes most of the code, the first reader of the docs is the agent, and the doc system is a routing system for that agent.** This post is the model. The next three cover routing, addressing, and lifecycle.

## 2. The first reader of the docs changed

Start with the scale. Over seven months the project had 3,614 commits. 1,373 of them touched docs or the entry file, and at least 547 carried an agent attribution (a lower bound, counted from the attribution line). As of October 14 the docs tree held 832 Markdown files, 51 structured change bundles (one change's requirements, design, implementation record, and test cases in a single directory — a bundle), and 301 early single-file plans.

Who reads these? At the start of every session the agent loads the entry file. Before it starts work it follows the entry to the specs. When it enters a module it opens the plans and the handoff records. My position is this: docs are now written for the agent first. What a human reads is what the agent produces at a decision point, not a cover-to-cover pass through the tree.

The opening thesis has to land on the properties of an agent. The whole mechanism is derived from the table below. Every principle later in the series is tagged with the property it answers.

| Agent property | What it requires of docs | Mechanism |
|---|---|---|
| No memory across sessions | Every session enters through the entry, so the entry must be a routing table | L0 + the "operation → required reading" table |
| Context is limited and it costs money | Tokens are the first cost; drill down on demand | L0–L3 layering, thin indexes |
| Follows the literal text and does not infer intent | Status, replacement, and scope are written out explicitly; "you might consult" becomes "you must read this before acting" | State machine, `Replaced by`, required-reading table |
| Can grep, glob, and run scripts | Names are pattern-matchable, metadata is parseable, rules can be linted | ID scheme, metadata block, doc-lint |
| **Is also the main author** | A convention that depends on good intentions will drift; a machine has to enforce it | Hook / CI checks |
| Several agents at once | A single entry; lessons live in the repo, not in a personal memory | One entry file (AGENTS.md) |

A word on the last two rows. "Is also the main author": the agent that writes the spec may be the same agent that violates it in the next session, so every convention a machine can check eventually becomes a check (hook / CI is the general shape; our project chose another enforcement point, saved for post 4). "Several agents at once": Claude Code, Codex, and Kimi took turns. A lesson that exists only in one agent's personal memory is gone the moment a different agent shows up.

### Code, tests, docs: three legs

**Code, tests, and docs are equally necessary. Drop one and the other two fail.** The agent writes the code. Tests prove the code is right. Docs tell the agent how to write it and where to write the result back. The three lock together: the routing table points the agent at the testing spec; the case index points tests back at requirements; doc-lint is "the test suite for docs." In the opening accident the tests and the testing spec were both there. What was missing was the one hop, inside the doc system, that puts the testing spec in front of the agent.

### Three corollaries

**Corollary 1: the human's role shifts from reader to adjudicator.** (Answers "is also the main author.") If the agent is the main author, the human no longer has to be the daily reader or the maintainer. The human shows up at decision points: approve a plan, make the call, accept a release seal, confirm a deliverable. The human reads the summary, the diff, and the conversation digest the agent prepared for that decision. The human does not browse the doc tree and does not maintain the docs. The quality of the decision then depends on what the agent puts on the table. A spec the agent never read will not appear in the summary or the checklist it prepared. Getting the agent to the right document is the precondition for a human decision.

**Corollary 2: a deliverable is not an engineering document.** (Answers "context is limited and it costs money.") User manuals, changelogs, and deployment handover notes are read by business users and by operations. They are product deliverables. The agent maintains them, but they do not enter the agent's routing system, or they only burn context. The routing table records only "after which operation this must be updated." We paid for leaving that row out: an approval flow went live on July 7, and the user manual was not updated until July 15. For eight days the flow list in the manual was wrong.

**Corollary 3: one document serves one reader.** (Answers "context is limited and it costs money.") A document that tries to serve both a human and an agent gets fat. Our plan index was supposed to answer only "where are the docs for this change." It was written as a progress board. The "next step" column averaged 98 characters, and the longest row was 1,128. Every time the agent opened the index it first had to swallow a page of progress narrative. The index is for the agent. When a human wants progress, the agent summarizes it on the spot, or a script generates a view.

## 3. Six symptoms

"The agent keeps forgetting things" is a vague complaint. Split open, it is six different failures. Each one happened in this project.

**Symptom 1: if it does not know which document to read, it reads none.** The opening release-seal accident is the type case. The spec was there. The path was not. An agent will not search the whole repo because "there ought to be a spec." If the path is not in the entry, it starts from common sense.

**Symptom 2: it reads an outdated plan and treats it as current fact.** The AI Quick Path at the top of the documentation-model spec says: when a document shows it has been superseded, jump first to the new document named by `Replaced by`. Of the 51 bundles, 35 did not write `Replaced by`, and 16 did not even have a Stable ID (the document's fixed number). The rule was there. The field was not. The rule spun in place. For an agent that follows the literal text, the absence of "superseded" means "still in force." Status itself was unreliable: the spec defines 8 statuses, and the index actually used 9 spellings.

**Symptom 3: it reads too much and drowns in history.** The entry file grew to 457 lines, mixed with a lot of incident narrative. The top of the roadmap stacked 34 date banners (progress announcements that start with a date, one on top of another) and became a second changelog. To start a small task the agent first had to load hundreds of lines of unrelated story, and the constraint that actually mattered was diluted.

**Symptom 4: a test case cannot be traced to its requirement.** The case index called itself "the single source of truth." In practice it was 28 stretches of narrative written batch by batch, plus two derived views kept in sync by hand. The three files together were 909 lines. When the agent wanted to know "which requirement is this case for" or "does this requirement have a case," it could only read the narrative and guess.

**Symptom 5: the work is done and nothing is written back.** 18 completed bundles had no `implementation.md`. How it was actually done, and where it departed from the plan, existed only in that session. The next agent could read the plan and could not tell that the plan had not been followed. The late user manual in corollary 2 is the same symptom landing on a deliverable.

**Symptom 6: each agent reads its own entry.** Before September 3 the entry file was named CLAUDE.md, after Claude Code's convention. Another tool will not necessarily load it. A separate batch of project-level lessons lived in one agent's personal memory, invisible to the others. Same repo, three agents, three different sets of "the project rules."

Set the symptoms next to the agent properties and they stop being mysterious:

| Symptom | The agent property behind it |
|---|---|
| Does not know which doc to read, so reads none | No memory across sessions |
| Treats an outdated plan as fact | Follows the literal text and does not infer intent |
| Drowns in history | Context is limited and it costs money |
| A case cannot be traced to its requirement | Can grep, but there is no relation field to grep |
| Finishes the work and does not write back | Is also the main author |
| Each agent reads its own entry | Several agents at once |

## 4. Root cause: the entry file became an encyclopedia

Follow the six symptoms to the bottom and two distinctions were never made.

**The first: resident versus on demand.** The entry file is loaded on every session. It is the most expensive place in the doc system. Every line is paid for, in tokens, on every session. Before the cleanup, the entry file held 9 "code review checks" and 7 "rule codified" marks, plus the incident stories behind them. A session that only changed button copy still had to load the code-review list and the database-migration pitfalls. The route that actually belonged there — "before a release seal, read this" — was absent (before September 18).

**The second: current fact versus history.** Current fact answers "what is true now" and is to be trusted. History answers "why it was like that then" and is to be checked. In our project the two were mixed. The project overview stopped on September 3, and several versions shipped after that without a change to it. In the refactoring track's roadmap, 8 titles were marked ✅ while the body said "not started." A human who reads that contradiction asks. An agent picks one of the two sentences and believes it.

Leave both distinctions unmade and the result is this: **the entry file became an encyclopedia, not a routing table.** An encyclopedia answers "what is it." A routing table answers "where do I read." An encyclopedic entry gets longer the more dutiful it is, and the longer it is, the harder it is to find the one line that matters. The opening accident is what happens when the encyclopedia never recorded the fact and the routing table did not exist.

## 5. Three principles

Work backward from the root cause and the model stands on three principles. Each one can be restated in a sentence. The parenthesis is the agent property it answers.

**Principle 1: the entry only routes. It does not carry content.** (Answers "no memory across sessions.") The entry is the one thing the agent is certain to read. Aside from a few hard rules, its job is to tell the agent "for this kind of work, read that document," not to move that document's content in. Content that has been moved in goes stale, swells, and finally drowns the route itself.

**Principle 2: the resident layer holds only rules that are too late to discover after the damage, and each rule carries one sentence of reason. Everything else is drilled into on demand.** (Answers "context is limited and it costs money." The half about the reason answers "follows the literal text and does not infer intent.") To decide whether something should be resident, ask only this: if the agent does not read it this session, will it cause damage before anyone notices? If yes, it stays resident. If no, it goes to L1 or below, and the routing table points at it when it is needed. The reason cannot be skipped. A command with no reason is dropped as soon as the literal wording fails to match. With a reason, the agent can infer the right move in a boundary case the rule does not cover. The full incident goes down to L2 / L3. The entry keeps the link.

**Principle 3: current fact and history live apart, and status and replacement are written as fields.** (Answers "follows the literal text and does not infer intent.") A human can hear "this one feels old" in the tone. An agent cannot. Whether a document is in force, and what replaced it, has to be a parseable field, not a narrative that has to be inferred. Writing it as a field also lets the agent grep it and lets a script check it. Posts 3 and 4 expand on that.

## 6. The model: four layers, L0–L3

The three principles, laid onto the doc structure, are four layers:

| Layer | Contents | When it is read | Constraint |
|---|---|---|---|
| L0 resident | Hard rules in the entry file + the routing table | Loaded automatically every session | Must stay short |
| L1 by work type | Specs (dev / test / DB / release seal / handbook / deploy) | Before starting, read only the one the routing table names | Shared layer + project layer |
| L2 by module / change | Plan bundles, long-running tracks, handoff docs | When entering that module | Has status and a replacement link |
| L3 evidence | Execution reports such as release-seal test reports, audit output | Drill down when evidence is needed | Does not serve as an entry |

**L0, resident,** holds two kinds of content: rules that are too late to discover after the damage (one sentence of rule, one sentence of reason, one link), and the routing table that tells the agent which L1 document each kind of work should open. It is loaded every time, so its only constraint is that it stay **short**. When several agents share the repo, there can be only one L0: a single entry file, AGENTS.md. Entry files required by other tools only forward to it (answers "several agents at once").

**L1, by work type:** development, testing, database, release seal, user manual, deployment. One spec per kind of work. Before starting, read only the one the routing table names. L1 splits into a shared layer and a project layer. The project layer declares which shared spec it inherits, and writes only this project's fill-in, current state, exceptions, and pitfalls.

**L2, by module / change:** a change's plan bundle, a long-running track, a handoff document. Read it only when entering that module. L2 goes stale by nature, so it must **have a status and a replacement link**.

**L3, evidence:** release-seal test reports, audit output, incident reports. Drill down only when evidence is needed. L3 **does not serve as an entry**. A rule that lives only in the conclusion of some report takes effect only when someone happens to read it.

The skeleton of an L0 entry file looks roughly like this (only the essential parts; the full template is left to the skill at the end of the series):

```markdown
# AGENTS.md — the only entry (loaded every session; keep it short)

## Hard rules (always in force)
- <one-sentence rule>. Reason: <one sentence>. Detail: <L1 link>

## Operation → required reading
| Operation | Required spec | One-sentence point |
|---|---|---|
| Release seal / produce a package / tag / say "full suite green" | <release-seal spec> | <one sentence of the full-suite definition> |
| DB schema / cross-environment data change | <project database spec> | <the single most important constraint> |

## Layered reading
L0 = this file, always in force. L1 = the table above, addressed by work type; before starting, read only the matching row.
L2 = the module's plan / track / handoff; read it when entering that module. L3 = evidence; drill down when needed.
If you cannot tell which document to read, read the table first, then look for the next index at the top of the matching spec.
```

Every L2 document carries a parseable metadata block at the top. That is where principle 3 lands:

```markdown
> Status: approved
> Stable ID: <T>-YYYYMMDD-NNN
> Replaces: none
> Replaced by: none
```

`Status` may take only a value from a fixed vocabulary. Free invention is not allowed. When a document is superseded, `Replaced by` is filled with the new document's Stable ID, and the agent jumps when it reads it.

The model leaves three questions, which are the next three posts:

| Question | Where it lands | Post |
|---|---|---|
| Which documents should be read? | The L0 → L1 route: the routing table, a single entry, two-layer inheritance | 2. Routing |
| Where do I look, and which copy do I trust? | Directories, IDs, bundles, indexes, status and the replacement chain | 3. Addressing |
| Where do I write, and how does it not rot? | Write-back, machine enforcement, memory layers, freshness | 4. Lifecycle |

## 7. The system was forced into existence by accidents

I should be plain about this: the four-layer model was not designed up front. It is the shape that became visible, looking back, after accident upon accident across seven months.

On March 4 the project was initialized. The entry file, CLAUDE.md, was 128 lines. The same day the rule that later mattered most was added, "plan-driven development": write the plan first, touch code only after it is confirmed, backfill the actual execution record when finished, and keep the roadmap current. From then on the docs grew with the development rhythm. Those early single-file plans number 301 today, and 218 of them were backfilled with an "actual execution record."

On May 26 the entry file was 302 lines. On August 20 it was 406. A large part of the growth was incident narrative: hit a pitfall, add a section to the entry file, write down what happened and what to do next time. Each section made sense alone. Together, the entry file became an accident manual that kept getting thicker.

September 3 was the first turning point. A documentation-architecture reshuffle touched 235 files. Test material scattered in four places was gathered into one. Plans were collected into three kinds: structured change bundles, long-running tracks, and early single-file plans. AGENTS.md became the only entry, and CLAUDE.md only forwarded to it. That eased "each agent reads its own entry" and "where does this go." It did not answer "which document should be read."

On September 18, after the opening release-seal accident, the "operation → required reading" table appeared for the first time, and the entry file started to have the shape of a route. On September 29 a database migration collided on its number. Two migrations with the same number had both already run in production. After the move-and-rework, the rule was "before taking a number, check every parallel branch and worktree." On September 30 an old package with the same name was deployed by mistake. After that, package names were required to carry the hour, minute, and second. On October 13 and 14, browser-automation (MCP) actions were treated as acceptance twice. The rule "MCP locates; it does not accept" was written and added to the routing table.

On October 14 the routing table grew into a layered-reading principle for L0 / L1 / L2 — the predecessor of the model in this post. The entry file was 457 lines. The same day the project opened a dedicated documentation-governance change (ID D-20261014-001), and this series was started at the same time. The result of that governance is in posts 3 and 4.

Laid out in order, the pattern is obvious: **almost every rule added later has an accident standing behind it.** The system was forced into existence by accidents. This series is written so the next project does not have to trade accidents for it.

## 8. Where each kind of document sits, who reads it, and what the human does

The model has to treat every document type the same way. The table below places fourteen common kinds into the four layers. In an agent-first system the human is not the daily reader of any of them, but every kind has a decision point where a human has to show up.

| Document | Layer | Who reads it | When | Human's role |
|---|---|---|---|---|
| Requirements | L2 | The agent implementing or reviewing the change | The first document read when entering the change | Confirm "what is wanted" before approval, and make the call on scope |
| Design | L2 | The agent implementing the change | Before implementation starts | Approve the plan, and make the call on design tradeoffs |
| Implementation record | L2 | The agent taking over, reworking, or tracing | On takeover; when asking "why was it done that way" | Read the deviation summary and confirm the departure is acceptable |
| Development spec | L1 | Every agent that writes code | Before starting, only the one the routing table names | Make the call on a new rule when an incident is codified |
| Refactoring track | L2 | The agent changing a related module | Read the historical lessons before entering the module | Make the call on track priority, on shelving, and on closing it |
| Testing spec | L1 | The agent writing, changing, or reviewing tests | Before touching tests | Make the call on the testing definition, such as which suites "full" includes |
| Case index | L2 | The agent changing a module or checking coverage | Before changing a module, look up existing cases and their source requirements | At acceptance, confirm whether a coverage gap is acceptable |
| Release-seal spec | L1 | The agent performing the release seal | Before a release seal, a package, or saying "full suite green" | Accept the release seal: walk the checklist and release on the evidence summary |
| Changelog | Deliverable | Business users | After a new version goes live, to see what changed | Confirm the deliverable: scope and wording match what shipped |
| User manual | Deliverable | Business users | While using the system or looking up a flow | Confirm the deliverable: spot-check that flows match the UI |
| DB spec | L1 | The agent changing table structure or cross-environment data | Before writing a migration script | Make the call on the compatibility rules and the exceptions |
| Migration index | L2 | The agent adding a migration or preparing a deploy | Before taking a number; before deploy, when listing the execution order | Before deploy, confirm the execution list the agent produced |
| Deployment runbook | L1 | The agent performing the deploy | Before deploying | Approve production; operations reads a separate handover note |
| Incident report | L3 | The agent investigating a similar problem or codifying a rule | Drill down when evidence is needed | Confirm the root cause, and decide whether to codify a rule and at which layer |

Three things are worth noticing. First, no cell in "when" says "anytime." Every document is bound to a trigger. That is what routing means. Second, the changelog and the user manual are not inside L0–L3. The agent maintains them and does not learn the job from them. When the agent traces "what changed in that version," it reads an L3 execution report such as the release-seal test report, not the changelog written for business users. Likewise, the deployment runbook is for the agent, and operations reads the handover note. One document serves one reader. Third, no cell in "human's role" says "maintain" or "read cover to cover." Every cell is approve, make the call, accept, or confirm.

## 9. How this model breaks

None of the following is hypothetical. Each one was the state of our project before the cleanup.

### Failure 1: L0 swells

The entry file's line count: 128 → 302 → 406 → 457. Look at the last stretch. After it became the only entry on September 3, and after the routing table was added on September 18, it **kept growing**.

The reason is plain. After each accident, the cheapest move is to add a section to the entry file. The review checks and the "rule codified" marks counted in the root-cause section accumulated that way. Each section is right on its own. The cost of L0 is a multiplication: lines times sessions. Worse, a swollen L0 drowns its own routing table, and the opening accident plays out again inside the file that holds the table. One detail: a heading in the entry file said "four pitfalls" and then listed 5 items. An inconsistency like that can sit forever in a file that is loaded every session, which means the file had grown past the point where anyone checked it line by line.

The direction of the fix: each L0 entry keeps one sentence of rule, one sentence of reason, and one link (principle 2), and the incident sinks. Links at the entry layer need a machine check. How to write the routing table so it does not itself grow into the entry file is the subject of post 2.

### Failure 2: the layer boundaries blur

If nobody guards the four boundaries, the layers seep into each other.

- **L1 mixed in templates and project adaptations.** The documentation-model spec itself was 1,123 lines. The shared spec, the project adaptation, and about 460 lines of templates sat in one L1 document, violating the "shared → project" layering that the same document had defined.
- **L2 long-running tracks swallowed short-term plans.** The refactoring track was supposed to be only a topic navigator. It held 145 single-file plans and a 2,613-line roadmap with status marks. The "title says ✅, body says not started" clash from the root-cause section lived here.
- **L2 and L3 were not separated.** The date banners at the top of the roadmap recorded the history of one release after another. They belonged in implementation records and in L3 execution reports. They piled up at the top of a current-fact document. The same set of release-seal numbers was repeated in four places: the index banner, the index row, the release documents, and the roadmap. Miss an update in one place, and the agent is looking at four versions of "the fact."

The sharpest of these is the first. The spec that defined the layers did not follow the layers itself.

### Failure 3: the agent that writes the docs is amnesiac too

Much of the swelling and the boundary crossing above was written by an agent following the spec. At the moment of writing it obeyed the rule it had read. It does not remember a convention another session settled last week, and it does not go back to check whether the whole system is consistent. The agent is "amnesiac" as a reader, and it is amnesiac as an author. A layering that is kept up by good intentions will drift. That is the subject of post 4: write-back is part of the change, conventions are enforced by a machine and the human only adjudicates, the entry layer has zero tolerance, and deeper layers have a baseline that may only fall, never rise.

## 10. Summary

1. The agent is not amnesiac. It never had memory across sessions. Every session is a newcomer coming in through the entry. Fix the entry, not the agent.
2. The first reader of the docs is the agent. The human shifts from reader to adjudicator. Deliverables are counted separately. One document serves one reader.
3. The entry only routes and does not carry content. The resident layer holds only rules that are too late to discover after the damage. Current fact and history stay apart, and status and replacement are written as fields.
4. The four-layer model: L0 resident (must stay short), L1 by work type (read only one), L2 by module / change (has status and a replacement), L3 evidence (never an entry).
5. The system was forced into existence by accidents, and it breaks on its own: L0 gets fat, boundaries blur, and the agent that writes the docs is amnesiac too.

### Series

1. Agents Aren't Amnesiac — They Can't Find the Entry Point: Documentation Layers for Large Projects (1) (this post)
2. [Make the Agent Read Only What It Should: Documentation Routing (2)](02-routing.md)
3. [Give Every Document Exactly One Place: Documentation Addressing (3)](03-addressing.md)
4. [Keep Documents from Rotting: The Document Lifecycle in the Agent Era (4)](04-lifecycle.md)
