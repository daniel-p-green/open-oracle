# Open Oracle: Legal, Privacy, Election-Information, and Accessibility Research

**Research cutoff:** laws and rules effective through **October 10, 2026**.  
**Prepared:** October 11, 2026.  
**Project assumed:** a nonpartisan voter-comprehension kiosk proof of concept in Jackson County, Missouri, with a Raspberry Pi performing local presence/wave detection; optional local wake-phrase detection; voluntary microphone interaction sent to an as-yet-unselected cloud AI provider; captions, translations and links to official sources; and optional thumbs-up/down helpfulness feedback.

**Purpose and limitation:** This is legal **issue-spotting research**, not legal advice, a legal opinion, or an assurance of compliance. Several conclusions turn on deployment facts that have not yet been selected—particularly the cloud vendor and contract, exact audio path, physical location, sponsoring/operator entity, government funding, retention configuration, age handling, and whether a kiosk will ever be placed at an election site.

**Download:** [Open Oracle legal/privacy/election/accessibility research — Markdown](sandbox:/mnt/data/open_oracle_legal_privacy_election_accessibility_research_2026-10-10.md)

## Executive brief and scope

The strongest caution is that **“Missouri is a one-party-consent state” is too crude a rule for Open Oracle**. Federal and Missouri interception statutes distinguish the *acquisition* of communications from saving a recording. Under federal law, “intercept” means the aural or other acquisition of communication contents through a device; a recording file need not be created. Federal law generally permits an interception when the interceptor is a party or one party gives prior consent, subject to the criminal/tortious-purpose exception. citeturn12view0turn13view0

Missouri is more textually awkward. RSMo §542.402 contains separate provisions concerning wire and oral communications. Its exception for a person acting under color of law expressly addresses **wire or oral communication**, while the private-person one-party-consent exception is textually written for **wire communication**. Missouri's oral-interception offense also contains device/transmission limitations. That means a private kiosk's ordinary microphone, local buffering, Wi-Fi and cloud transport need to be analyzed as an actual technical flow rather than classified by slogan. citeturn0search6turn0search9 **Confidence: high** that the statutory distinction exists; **moderate** on how a court would classify this particular architecture without more facts.

For a controlled demonstration, the minimum-risk approach is therefore to keep the microphone **off by default**, require a deliberate opt-in immediately after a short disclosure, preferably use push-to-talk or a tightly bounded listening interval, display an unmistakable live-microphone indicator, and avoid capturing surrounding conversation. A locally processed wake phrase is safer than continuously streaming ambient audio to a cloud provider, but it does **not** make the pre-wake acoustic acquisition legally nonexistent. That conclusion follows from the statutes' acquisition-based definitions. citeturn12view0turn0search9

The camera presents a substantially different risk profile if it truly performs only local, ephemeral presence/wave detection and does not save frames, identify a person, perform face recognition, generate persistent embeddings, recognize gait, or build identity profiles. Missouri has at least **sector-specific** biometric legislation—RSMo §302.170 regulates biometric information in Department of Revenue driver-license/identification functions—but that statute does not on its face create a generally applicable private-sector biometric regime for a voter-information kiosk. citeturn19view2 I did **not** locate a generally applicable Missouri comprehensive consumer-privacy statute or broad biometric privacy act in the official Missouri sources reviewed through the research cutoff. That finding must be treated as an incomplete-search result, **not permission** and not a representation that no common-law, constitutional, consumer-protection, contractual, municipal, or newly enacted/uncodified rule can apply. **Confidence: moderate.**

Children create a separate federal issue. Current COPPA regulations define a child as under 13 and include a photograph, video, or audio file containing a child's image or voice, persistent identifiers, and recognition biometrics in “personal information.” COPPA ordinarily requires parental consent for a covered operator, although the current rule contains narrow exceptions—including a tightly constrained voice-audio response exception. COPPA's operator definition is tied to commercial online services and excludes nonprofits that would otherwise be outside FTC Act §5 coverage, so direct applicability can differ materially among a private commercial operator, qualifying nonprofit, government body, and cloud vendor. citeturn19view0 **Confidence: high** on the rule; **moderate** on Open Oracle until the operator/vendor structure is fixed.

Government sponsorship materially changes the risk picture. Missouri's Sunshine Law expressly defines “public record” to include electronically stored records retained by or of a public governmental body and records created or maintained by private contractors under agreement with, or on behalf of, the public body. Vendor-hosted prompts, transcripts, feedback and logs therefore cannot safely be treated as “private vendor data” merely because they reside in the cloud. citeturn13view1 Section 610.021 contains specific categories that may be closed—including certain security-system and network-configuration information and records protected from disclosure by other law—but does not provide a general exemption for private or embarrassing kiosk conversations. citeturn13view2

Election-law risk is particularly location-sensitive. Missouri amended RSMo §115.637 effective **August 28, 2026**. During election day and the absentee-voting period, subsection (18) bars a list of activities—including **exit polling, surveying, sampling and electioneering**—inside the polling-place building or within 25 feet of the closest outer door. An election authority may, after the required advance posting, extend most of that restriction to **50 feet**. citeturn16view0 Because “surveying” is separately enumerated, even a benign thumbs-up/down question about whether the explanation was helpful creates an avoidable issue near a polling place. The low-risk rule is to disable feedback and keep the kiosk outside the applicable buffer unless the responsible election authority and counsel approve a different arrangement.

For publicly funded deployments, Missouri's newly effective §115.646 prohibits officers, employees and agents of political subdivisions, special districts and charter schools from making a contribution or expenditure of public funds to advocate, support or oppose a ballot measure or candidate. The current version became effective **August 28, 2026**. citeturn15view1 A genuinely neutral explainer is very different from advocacy, but “nonpartisan” branding cannot rescue substantively slanted content.

Accessibility also changed during 2026. DOJ's Title II web/mobile rule still specifies **WCAG 2.1 Level AA**, but an April 2026 Interim Final Rule extended the compliance dates to **April 26, 2027** for public entities with populations of 50,000 or more and **April 26, 2028** for smaller entities and special district governments. citeturn18view0 The extension does **not** postpone existing Title II duties of effective communication, reasonable modification and equal opportunity. citeturn18view0turn18view2 Nor should the freestanding kiosk automatically be assumed to fall inside or outside the web/mobile technical rule; its software architecture matters.

**Overall confidence:**  
**High** on the quoted federal statutes, current Missouri statutes and DOJ's 2026 ADA date change.  
**Moderate** on statutory application to Open Oracle because architecture/operator/location facts remain open.  
**Low to unknown** on completeness of local Jackson County/Kansas City ordinance coverage, final vendor obligations, specific public-record retention schedules, and current Voting Rights Act language-coverage status until those are independently resolved.

## Requirements and applicability matrix

| Area | Law, rule, or guidance | Trigger for Open Oracle | Requirement / consequence | Citation and effective status | Uncertainty |
|---|---|---|---|---|---|
| Federal microphone interception | **Binding federal law** | Intentional acquisition of protected wire, oral or electronic communication | “Intercept” is acquisition; saving a recording is not required. A private party may generally intercept when it is a party or one party gives prior consent, unless done for a criminal or tortious purpose. | 18 U.S.C. §§2510(2), (4), 2511(1), 2511(2)(d). citeturn12view0turn12view1turn13view0 | Whether ambient bystander speech qualifies as a protected “oral communication” depends partly on justified expectation of non-interception. |
| Missouri microphone interception | **Binding state law** | Microphone acquisition in Missouri; classification as wire/oral; private versus governmental actor; device/transmission facts | Do not reduce §542.402 to “one-party consent.” Missouri's private-person and color-of-law exceptions are textually different, especially as to oral communications. | RSMo §§542.400, 542.402; §542.400 page also notes *Angel v. Williams*, 12 F.3d 786 (8th Cir. 1993). citeturn0search9turn0search6 Effective dates shown by Revisor: §542.400 Aug. 28, 2002; §542.402 Jan. 1, 2017. | **Material.** Exact microphone, pre-buffer, Wi-Fi/radio and cloud path should be reviewed by Missouri counsel. |
| Bystander audio | **Federal/state interception law** | Kiosk hears speech that was not directed to it | Active participant's consent does not logically supply consent by a separate bystander. Public setting affects expectation analysis but is not a categorical consent substitute. | Federal “oral communication” definition requires an expectation under circumstances justifying it. citeturn12view0 Missouri Revisor's *Angel* annotation involved a public-jail setting. citeturn0search9 | Highly fact-specific. |
| COPPA | **Binding federal regulation when operator is covered** | Covered commercial online service directed to under-13s, or actual knowledge that PI is being collected from a child | Child voice/image files, persistent identifiers and recognition biometrics are PI; notice/VPC normally required, subject to exceptions. | 16 CFR §§312.1–.5. Current eCFR was up to date through Oct. 7, 2026 and incorporates April 22, 2025 amendments. citeturn19view0 | Operator/nonprofit/government/vendor status is important. |
| COPPA voice exception | **Binding federal regulation when COPPA applies** | Collection of child's voice audio solely to answer specific request under §312.5(c)(9) | Exception is narrow; the current rule also requires disclosure in the online notice of how the audio is used and that it is immediately deleted after responding. citeturn19view0 | 16 CFR §§312.4(d), 312.5(c)(9), as amended in 2025. | Cloud processing may or may not count as “disclosure”; qualifying support-for-internal-operations providers are treated specially under §312.2. |
| Missouri breach notification | **Binding state law** | Operator owns/licenses defined statutory PI and a qualifying breach occurs | Missouri's definition is considerably narrower than everyday “personal data”; specified sensitive information is required. Processor/maintainer duties and owner/licensee notice can apply. | RSMo §407.1500, effective Aug. 28, 2009. citeturn19view1turn0search3 | Free-form voice can unexpectedly contain statutory PI even if the kiosk never requests it. |
| Missouri biometrics | **Binding but sector-specific state law** | DOR driver-license/ID biometric functions | §302.170 regulates DOR biometric use and contains biometric definitions, including specified voice comparison. | RSMo §302.170, effective Aug. 28, 2020. citeturn19view2 | Does **not** itself establish a general biometric-kiosk statute. Broader/local rules remain a research gap. |
| FTC biometric/privacy practices | **Agency policy/enforcement guidance, not standalone biometric legislation** | Private entity within FTC jurisdiction; privacy/security representations or potentially unfair practices | Avoid surreptitious or unexpected biometric collection, weak risk controls and misleading privacy/accuracy representations. | FTC biometric policy statement, May 18, 2023. citeturn4search1 | FTC jurisdiction depends on operator; governmental bodies are a different analysis. |
| Missouri Sunshine Law | **Binding state law for covered government bodies** | County/city/state/election-authority sponsorship or contractor maintaining records on its behalf | Contractor-held electronically stored records can be public records. | RSMo §610.010(6). citeturn13view1 | Exact retention and disclosure treatment of each kiosk artifact requires records counsel. |
| Sunshine exemptions | **Binding state law** | Government record falls within enumerated closed-record category | Security/network and records-protected-by-law exemptions exist, but they are specific—not a blanket conversational-privacy exemption. | RSMo §610.021(14), (19)–(22), current section effective Aug. 28, 2025. citeturn13view2 | Do not promise confidentiality/deletion until records classification is complete. |
| Public-funds election neutrality | **Binding Missouri election law** | Public funds from political subdivision/special district/charter school | Public funds may not advocate, support or oppose candidate/ballot-measure outcomes. | RSMo §115.646, effective Aug. 28, 2026. citeturn15view1 | Neutral education/advocacy boundary depends on actual content and purpose. |
| Polling-place activities | **Binding Missouri election law** | Election day/absentee-voting period near polling place | Baseline 25-foot zone; local election authority can expand listed activities to 50 feet after notice. “Surveying” and “electioneering” are independently enumerated. | RSMo §115.637(18), effective Aug. 28, 2026. citeturn16view0 | Neutral AI explanation is not expressly classified; safest placement is outside the applicable zone. |
| Misleading sample ballots/interference | **Binding Missouri election law** | Kiosk reproduces something presented as sample ballot or interferes with voter | False/fraudulent or intentionally misleading sample ballots and interference inside polling place are specifically prohibited. | RSMo §115.637(2), (3), (16), (17). citeturn15view2turn16view0 | Ordinary explanatory text is not automatically a “sample ballot.” |
| Missouri campaign finance | **Binding state law** | Spending/contributions undertaken for purpose of influencing/supporting/opposing candidate or measure | “Committee,” “contribution” and “expenditure” definitions are purpose-focused. | RSMo §130.011(7), (12), (17), effective Aug. 28, 2025. citeturn15view0 | Funding, coordination, sponsor messaging and content determine whether registration/reporting/attribution questions arise. |
| Voter intimidation | **Binding federal law** | Conduct intimidates, threatens or coerces voting or assistance with voting | Applies to public and private actors under VRA §11(b). | 52 U.S.C. §10307(b); 18 U.S.C. §594 also addresses voter intimidation in federal-election context. citeturn16view1turn16view2 | Surveillance-like UX can create serious factual risk even without collecting vote preferences. |
| ADA Title II | **Binding federal law/regulation** | State/local government provides or contracts for kiosk service | Program/service must provide equal access, effective communication and reasonable modifications. Contractors do not remove the public entity's obligations. | DOJ Title II guidance. citeturn18view0turn18view1turn18view2 | Exact kiosk technical requirements depend on installation/software. |
| Title II web/mobile rule | **Binding federal regulation** | Government-provided web content/mobile applications | WCAG 2.1 AA; after 2026 IFR, deadlines are Apr. 26, 2027 for 50,000+ and Apr. 26, 2028 for smaller/special-district entities. | 28 CFR Part 35 Subpart H; DOJ 2026-updated fact sheet. citeturn18view0turn18view3 | Freestanding kiosk UI is not automatically within this specific subpart. |
| ADA Title III | **Binding federal law/regulation** | Private entity operating goods/services of covered place of public accommodation | Nondiscrimination and effective-communication/auxiliary-aid duties may apply. | 42 U.S.C. §12182; 28 CFR Part 36. | Invite-only prototype facts differ from an unattended public service. |
| Section 504 | **Binding federal statute when trigger exists** | Program or activity receives federal financial assistance | Disability nondiscrimination applies to covered recipient's program/activity. | [29 U.S.C. §794](https://www.law.cornell.edu/uscode/text/29/794). | Federal funding and recipient/contractor relationship must be established. |
| Language assistance | **Multiple possible legal sources** | VRA §203 coverage and/or federal financial assistance under Title VI implementation | Translation obligations should be analyzed separately from ADA disability access. | [52 U.S.C. §10503](https://www.law.cornell.edu/uscode/text/52/10503); [42 U.S.C. §2000d](https://www.law.cornell.edu/uscode/text/42/2000d). | I did not independently establish current Jackson County §203 coverage in this research; treat it as unresolved. |

## Detailed legal analysis

**Microphone capture, streaming and recording.** Federal law makes the capture/storage distinction unusually important here. Section 2510(4) defines an interception as the “aural or other acquisition” of contents through an electronic, mechanical or other device. Section 2511(1)(a) prohibits intentional interception subject to exceptions. Nothing in that definition requires creation of a durable WAV, MP3 or transcript. A microphone feeding an in-memory speech recognizer or sending packets to a cloud speech/AI service can therefore present an interception question even if the operator never exposes a “Record” button. citeturn12view0turn12view1

Federal §2511(2)(d) gives private actors a significant exception: an interception is not unlawful under that chapter when the interceptor is a party to the communication or one of the parties gave **prior consent**, unless the interception is for the purpose of committing a criminal or tortious act. Government/color-of-law actors have a parallel one-party provision in §2511(2)(c). citeturn13view0 For Open Oracle, an on-screen disclosure followed by a deliberate **Start voice** action provides much cleaner evidence of prior consent than an always-listening mic plus distant signage.

The active visitor and nearby strangers should be analyzed separately. A visitor intentionally addressing Open Oracle can consent to the kiosk's capture of that interaction. Two people speaking privately to each other six feet away have not thereby become parties to the kiosk interaction. Federal protection for an “oral communication” does turn partly on whether the speaker exhibited an expectation against interception under circumstances justifying that expectation, so setting matters. citeturn12view0 But a rule that “everything spoken in public may be captured” goes beyond the statutory text.

Missouri's statute makes an even stronger case for conservative engineering. The current Missouri provision does **not** simply say “any person may record a conversation with one-party consent.” Section 542.402.2(2), covering a person acting under color of law, expressly refers to intercepting a **wire or oral communication** with one-party consent. Section 542.402.2(3), for a person not acting under color of law, is textually phrased in terms of a **wire communication**, subject to its criminal/tortious-purpose limitation. Missouri's oral-interception offense also contains particular device/transmission elements. citeturn0search6 This is a meaningful statutory ambiguity for a privately operated Raspberry Pi whose microphone initially receives speech acoustically and then transmits it over a digital network.

Missouri's definition provisions and official Revisor annotations also reinforce that context matters. The Revisor page notes the Eighth Circuit's *Angel v. Williams*, 12 F.3d 786 (8th Cir. 1993), involving city officials' recording of officers in a public jail and concluding, on those facts, that the officers could not justifiably expect privacy. citeturn0search9 That is useful precedent for the expectation element; it is **not** a general license to capture every conversation occurring in a public building.

**Practical consequence:** Missouri counsel should be shown the literal audio diagram, not a prose description. The diagram should identify microphone hardware, analog/digital conversion, ring-buffer length, wake-word model, whether the Pi keeps PCM samples before activation, whether the stream travels by Wi-Fi/Bluetooth or wired Ethernet, where speech-to-text occurs, which vendor receives audio versus text, what is persisted, and when buffers are overwritten. **Confidence: high** that these distinctions matter; **moderate** on the ultimate Missouri classification.

A **local wake phrase** reduces risk if no pre-activation sound leaves the Pi and buffers are extremely short and automatically overwritten. But local processing is still processing. The acquisition-based definitions mean “we don't save it” and “we don't send it to the cloud” are useful minimization facts, not complete statutory answers. citeturn12view0turn0search9 The lower-risk public architecture is a physical/touch control as the ordinary activation mechanism, with wake phrase optional rather than required.

For bystanders, use engineering controls rather than legal presumptions: a close-talk or narrow-beam microphone, low gain, short session windows, conspicuous **MIC LIVE** indication, automatic termination when the user steps away, and no background speech logging. Those are recommendations rather than independently enumerated statutory requirements, but they reduce the chance that the system ever acquires a separate protected conversation.

**Camera, presence detection and biometrics.** On the described facts, presence/wave detection can be architected without identity processing: a camera frame exists ephemerally in memory, a local model outputs something such as `person_present` or `wave_detected`, and no frame, face vector, gait signature or cross-session identifier is stored. That is materially different from face recognition or identity matching.

Missouri's RSMo §302.170 demonstrates that state law specifically regulates biometric data in at least one sector. In the Department of Revenue context, its biometric definition reaches, among other modalities, voice information used to compare live speech with a previously created speech model. citeturn19view2 That statute is tied to driver's-license/identification functions and is not a general biometric privacy statute applicable to Open Oracle merely because the kiosk has a camera or microphone.

COPPA's current definition is useful for understanding the identity distinction as well. For covered children's services, a “biometric identifier” includes data capable of automated or semi-automated recognition of an individual, with examples such as voiceprints, gait patterns, facial templates and faceprints. citeturn19view0 A generic model that answers only “did somebody wave?” is not the same thing as a facial template used for recognition. That does not make the underlying camera use consequence-free; it means the biometric trigger is materially less obvious.

The safest public description is narrowly factual: *“The camera is processed on this device to detect whether someone is present and intentionally waves. It does not identify you, recognize your face, create a face or voice template, or save images.”* Each sentence should be used only if engineering tests and logs establish that it is true. FTC policy has specifically warned about deceptive or unexpected biometric practices, so overpromising privacy can itself create risk for covered commercial operators. citeturn4search1

I did **not** locate a generally applicable 2026 Missouri biometric privacy statute comparable to Illinois BIPA, nor a statewide comprehensive consumer privacy act clearly governing this kiosk, in the official Missouri materials reviewed. **Confidence: moderate rather than high**, because a comprehensive negative proposition requires exhaustive session-law/local-code reconciliation. The deployment checklist should include a final Revisor/session-law check and local-code check immediately before launch.

**Children and COPPA.** Current 16 CFR Part 312 defines a child as under 13 and defines “personal information” to include persistent identifiers such as IP/device identifiers, a photograph/video/audio file containing a child's image or voice, and biometric identifiers used for recognition. citeturn19view0 Covered operators ordinarily must provide notice and obtain verifiable parental consent before collecting, using or disclosing such information. citeturn19view0

The operator definition is important: COPPA's regulation addresses a person operating an internet website or online service in commercial interstate/foreign commerce and expressly excludes nonprofit entities that would otherwise be exempt from FTC Act §5. citeturn19view0 A county government itself is therefore not analytically interchangeable with a private commercial vendor operating the kiosk. A public/private partnership can require separate analysis of each entity's role.

The current rule has a narrow voice exception in §312.5(c)(9), added by the 2025 amendments. The accompanying current notice requirement says an operator using that provision must describe how the child's voice audio is used and state that the files are deleted immediately after responding to the request. citeturn19view0 The rule also defines “disclosure” so that qualifying providers supporting internal operations are treated differently from independent third parties. citeturn19view0 Consequently, “we use cloud AI” does not by itself answer whether the exception can apply; the cloud provider's purposes, retention, training, profiling and contractual role matter.

For an unattended first public version, the cleaner policy is to make **under-13 voice unavailable** unless the team deliberately builds and has counsel review a COPPA pathway. Text and accessible nonvoice functionality should remain available. That recommendation avoids having kiosk staff or an AI model guess children's ages from appearance or voice, which would create its own problems.

**Cloud processing, training, retention and breach obligations.** No selected vendor means there is currently no defensible statement such as “the AI provider does not train on this data,” “audio is retained for zero days,” or “everything is deleted immediately.” Those are vendor/product/account/contract/configuration facts, not inherent properties of “cloud AI.”

The production data-flow review should separately identify raw audio, speech-to-text output, user text, model input, system instructions, model output, abuse/safety monitoring records, network/IP metadata, telemetry, crash reports, administrator logs, feedback and backups. For each, establish who receives it, for what purpose, whether the vendor is allowed an independent use, retention period, deletion mechanics, subprocessors, encryption, geographic location, human access and legal-hold exceptions.

Missouri's breach statute is narrower than a modern comprehensive privacy act. RSMo §407.1500 covers defined “personal information,” including specified combinations involving an individual's name and sensitive elements such as Social Security number, government identification, financial credentials, medical information and health-insurance information. It also imposes notification relationships between maintainers/processors and owners/licensees. citeturn19view1turn0search3 An anonymous sentence such as “What time do polls open?” is therefore not automatically statutory “personal information” for §407.1500 merely because it is personal data in a colloquial sense.

Free-form speech changes the practical picture: a visitor can volunteer a full name, driver's-license number, medical condition or financial credential even if Open Oracle never asks. The system should prominently tell users **not to speak sensitive identifiers**, avoid logging raw conversation by default and consider redaction before any troubleshooting log is created.

A government operator has an additional public-record problem. Missouri's definition of public record expressly encompasses records created or maintained by private contractors under an agreement with a public governmental body or on its behalf. citeturn13view1 Thus, “the county never stores the transcript; Vendor X does” does not necessarily take the transcript outside Chapter 610.

Section 610.021 allows particular records to be closed. Relevant examples include records protected from disclosure by other law, specified security information and records revealing system/network configuration in a manner that would facilitate unauthorized access or disruption. citeturn13view2 Those provisions should protect genuine security material where their elements are satisfied, but they should not be treated as a general-purpose exemption for voter questions.

The exact **records-retention schedule** for prompts, transcripts, feedback, telemetry and vendor logs was not successfully verified from a sufficiently specific official Missouri/local retention source in this research. That is a **deployment-blocking unresolved fact for government sponsorship**, not evidence that the records may simply be deleted at will. Public records counsel/records officers should classify each data artifact before a government privacy notice promises immediate destruction.

Government procurement can add duties even where no statute directly specifies a cloud-AI retention period. Accessibility clauses, security requirements, incident notification, audit rights, public-record cooperation, data ownership, subcontracting, insurance, indemnity and deletion can arise from procurement rules, policies and the negotiated agreement. Because neither the governmental sponsor nor vendor has been selected, this report does not characterize any such provision as presently binding.

**Neutral election information, advocacy and accuracy.** Missouri's campaign-finance definitions focus on purpose. A “committee” generally involves receiving contributions or making expenditures for the primary or incidental purpose of influencing voters for or against candidates or ballot measures. “Contribution” and “expenditure” similarly use supporting/opposing concepts. citeturn15view0 A genuinely neutral explanatory tool—with equivalent treatment, official-source grounding, no voting recommendation and no campaign coordination—is therefore materially different from political advocacy.

Neutrality nevertheless needs operational definition. An AI system can become functionally partisan by selecting favorable facts for one candidate, using emotionally different language, generating recommendations, adopting a campaign's framing, selectively refusing criticism, or consistently hallucinating against one side. A content policy should require the same explanation structure for every candidate and measure, explicit sourcing, visible dates, no “who should I vote for?” recommendations, and escalation when official sources conflict.

Where **public funds** are involved, §115.646 deserves a separate control. As amended effective August 28, 2026, it bars specified political-subdivision actors from contributions or expenditures of public funds to advocate, support or oppose passage/defeat of a ballot measure or nomination/election of a candidate. citeturn15view1 Government sponsorship should therefore include a documented neutral-content standard and review process.

Missouri also expressly criminalizes printing/circulating false and fraudulent sample ballots designed to defraud voters and purposefully giving a written sample ballot intended to mislead a voter. citeturn15view2 Open Oracle need not become a “sample ballot” simply by explaining measures, but if it displays an imitation ballot or labels generated material “sample ballot,” counsel should evaluate these provisions closely.

For changing election facts—deadlines, poll locations, registration status, ballot wording—the kiosk should prefer deterministic retrieval from the responsible official source over open-ended model recollection. Missouri's Secretary of State says statewide elections are administered in a decentralized system of **116 local election jurisdictions**, with local authorities conducting elections and voter-registration functions. citeturn21search16 An AI answer should therefore know which authority governs the specific address before presenting local operational information.

Jackson County has a particularly important split. The Jackson County Board of Election Commissioners states that it is the election authority for Jackson County **outside the corporate limits of Kansas City, Missouri**; residents inside Kansas City use the Kansas City Board of Election Commissioners. citeturn21search0turn21search3turn21search27 A countywide deployment cannot have a single undifferentiated “Jackson County election authority” source.

**Polling locations and electioneering.** Section 115.637(18), as amended in 2026, applies on election day and during the absentee-voting period. It lists exit polling, surveying, sampling, electioneering, distribution of election literature, posting signs, petitioning and certain sign-bearing vehicles, and sets a 25-foot baseline from the polling building's closest outer door. The election authority can increase most listed activities to 50 feet if it posts the required notice no later than six weeks before the election. citeturn16view0

This has two implications for Open Oracle:

First, do not assume that “neutral” equals safe inside the zone. The statute separately names **surveying**, so the optional helpfulness question can create a problem independent of whether the explanation advocates anything. citeturn16view0 Disable feedback entirely in a polling-place deployment.

Second, the applicable distance cannot be hard-coded statewide at 25 or 50 feet. The statute creates a baseline and an authority-specific expansion mechanism. Ask the relevant board whether it made the statutory election-specific posting and obtain the site map/measurement in writing.

Section 115.637 also prohibits interfering or attempting to interfere with a voter inside a polling place and disruptive/threatening activity that impedes registration, election, counting or verification. citeturn16view0 The safest first deployment is therefore **not inside an operating polling place at all**. A library, civic building or other voter-information site outside election operations eliminates a large category of risk.

Federal voter-intimidation law supplies an additional backstop. Section 11(b) of the Voting Rights Act provides that no person, whether acting under color of law or otherwise, may intimidate, threaten or coerce, or attempt those acts, for voting, attempting to vote or urging/aiding another person to vote. citeturn16view1 Do not make the kiosk look like surveillance or eligibility enforcement: no collection of voting preference, no individualized political inference, no face/voice identification, and no UI implying that use is required before a person may vote.

**Sponsor identification and official-affiliation claims.** The Chapter 130 material verified in this research establishes campaign-finance triggers but did not provide enough primary-source support for me to state a universal “paid for by” requirement for a genuinely neutral Open Oracle kiosk. Where the funding/content becomes advocacy within Chapter 130, Missouri Ethics Commission/counsel should determine the exact registration, reporting and attribution rules. citeturn15view0

Regardless of whether a campaign disclaimer is legally required, the kiosk should visibly identify its **actual operator and sponsor**. Do not call it an “official Jackson County voting kiosk,” use election-authority seals/logos or say it is “approved by JCEB/KCEB” unless the relevant authority has given written authorization. I did not identify a Missouri election provision that universally prohibits every possible false-affiliation statement, so this is deliberately framed as a **misrepresentation/branding/agency risk control**, not as an invented election statute.

**Corrections and disclaimers.** No source reviewed establishes a general Missouri statute requiring an AI election explainer to maintain a particular correction SLA. The appropriate safeguard is nevertheless strong: every answer involving election procedure should expose its authoritative source and effective/as-of date; uncertain or conflicting information should produce a refusal/escalation rather than an invented reconciliation; and urgent election-authority corrections should be deployable without a model retraining cycle. A “not official” disclaimer does not cure false operational information, electioneering, public-fund advocacy or intimidation.

**Disability access.** If Jackson County, Kansas City, an election board or another state/local entity provides the kiosk as its service, **ADA Title II** is the primary federal framework. DOJ's guidance states that Title II covers all state and local government services, programs and activities, and that using contractors does not eliminate those responsibilities. citeturn18view0turn18view1

General Title II requirements exist today regardless of the web-rule deadline. DOJ states that governments must provide effective communication, reasonable modifications and equal opportunity even when a specific web-content exception applies. citeturn18view0turn18view2 Open Oracle therefore should not force any person to see a camera cue, wave an arm, hear speech, speak clearly or operate precise touch targets as the only way to receive election information.

The interface should provide functionally equivalent routes: visible large-button activation plus keyboard/switch-compatible activation; text as a complete alternative to voice; captions for all generated speech; repeat/pause/volume controls; no audio-only status information; no gesture-only commands; stable focus and navigation; generous timeouts with extension; undo/back; and direct access to official source text. For blind and low-vision users, structured screen-reader output and nonvisual navigation should be designed from the beginning rather than layered on later. For people with mobility disabilities, the physical mounting should be usable from a seated position with adequate clear floor space and controls that do not require fine motor gestures. These design choices support existing effective-access duties, while the exact 2010 ADA Standards provisions applicable to a freestanding kiosk should be confirmed for the final installation. citeturn18view1turn18view2

For cognitive accessibility, plain language, short explanations, predictable navigation, explicit “show me the official wording” controls and easy correction are strong practices. This report does **not** characterize “plain language” as a universal standalone statutory kiosk mandate; its legal relevance is through equal/effective access and reasonable-modification analysis in context.

A major 2026 update prevents a common date error. DOJ's 2024 Title II rule established WCAG 2.1 AA for state/local **web content and mobile apps**, but DOJ's April 20, 2026 Interim Final Rule extended the deadlines. The current dates are **April 26, 2027** for entities with population 50,000 or more and **April 26, 2028** for entities below 50,000 and special district governments. citeturn18view0 Any report still stating that a 50,000+ public entity's deadline was April 2026 is outdated as of the requested cutoff.

That rule's specific technical scope should not automatically be stretched to every interactive machine. DOJ defines the rule around web content and mobile applications; mobile apps are downloaded applications designed to run on mobile devices such as smartphones/tablets. citeturn18view0 A Raspberry Pi running a wholly local native application may therefore present a different Subpart H question from a kiosk whose UI is literally government web content loaded from a website. **Use WCAG 2.1 AA as an engineering baseline either way**, while counsel determines what is legally mandatory.

For a privately operated public deployment, ADA **Title III** may apply through the owner/operator/lessor/lessee of a covered place of public accommodation and the goods/services offered there. A private invitation-only hackathon is not analytically identical to an unattended kiosk offered to the general public.

Section 504 adds another layer if the relevant program or activity receives federal financial assistance. [29 U.S.C. §794](https://www.law.cornell.edu/uscode/text/29/794) is therefore a funding-trigger question, not a rule that automatically attaches to every privately funded prototype.

HAVA's voting-system accessibility requirements should not automatically be imported into an informational kiosk merely because its subject is voting. [52 U.S.C. §21081](https://www.law.cornell.edu/uscode/text/52/21081) concerns voting-system requirements. If Open Oracle ever becomes functionally integrated into the voting system rather than remaining an independent informational tool, that conclusion should be revisited.

**Translation and language assistance.** Language assistance is legally distinct from disability access. Voting Rights Act §203 imposes minority-language election-material requirements in jurisdictions covered by the statutory/Census determination process, while Title VI and implementing guidance can create language-access obligations for federally funded programs. [52 U.S.C. §10503](https://www.law.cornell.edu/uscode/text/52/10503); [42 U.S.C. §2000d](https://www.law.cornell.edu/uscode/text/42/2000d).

I did **not** independently verify the currently operative §203 determination for Jackson County/Kansas City from a sufficiently specific Census primary source in this research. That remains unresolved and should **not** be interpreted as “Jackson County is not covered.” Even where translation is voluntary rather than mandated, ballot terminology should use authoritative translated material where available and human-reviewed terminology rather than unconstrained model paraphrase.

**Private hackathon tonight versus unattended/public/government deployment.** These are not merely different scale levels.

A staffed prototype with known consenting adults can control age, notice, microphone radius, session duration and bystander proximity; can avoid election premises; and can immediately stop a malfunctioning sensor. A public kiosk has unknown ages, unpredictable bystanders, accidental sensitive disclosures, accessibility needs, physical tampering, vendor logging, changing election facts and unattended failures.

Government sponsorship adds a second layer: public-funds neutrality under §115.646; Sunshine Law/public-record handling; records retention; Title II; procurement requirements; possible §504/Title VI funding conditions; and heightened consequences if the public reasonably understands the kiosk as official. citeturn15view1turn13view1turn18view0

The practical dividing line is therefore:

| Controlled private demo | Unattended/public or government deployment |
|---|---|
| Identified consenting adults | Unknown users including minors |
| Staff controls mic/camera context | Ambient bystanders and unattended capture |
| Temporary, controlled venue | Public-space privacy expectations vary |
| Can use text fallback if cloud terms are unknown | Vendor contract/settings must be resolved in advance |
| No reason to be at a polling place | Election-site buffers and authority jurisdiction become central |
| Accessibility can be actively assisted, although applicable venue/service law remains | Independent accessible use must be designed into the system |
| Demo data can be eliminated by design | Government records/retention may restrict deletion |
| “Prototype” status obvious to participants | Official-affiliation ambiguity becomes much more serious |

## Must do tonight

These are **minimum-risk prototype controls**, not a declaration that the demonstration thereby complies with every applicable law.

**Must do tonight — microphone and privacy.** Limit the interactive voice demonstration to consenting adults. Keep the microphone disabled at idle. Before activating it, display a short notice that voice will be captured and, if applicable, sent to a named cloud service; require a deliberate **Start voice** or push-to-talk action. Display a persistent live-mic indicator and terminate capture promptly when the utterance ends. This aligns the technical flow with the federal requirement of prior consent and avoids depending on Missouri's ambiguous private-actor oral-interception treatment. citeturn13view0turn0search6

Do **not** turn on an always-listening wake phrase tonight unless it is essential to the proof of concept and you have personally verified that the pre-wake buffer is strictly local, very short, not written to disk and never transmitted. A button/touch activation demonstrates the product concept with materially less unresolved audio law.

Use a directional/close-talk microphone, keep spectators several feet away and pause voice capture whenever nearby people are having unrelated conversations. Active-user consent should not be treated as bystander consent.

If the cloud vendor/product/account configuration is not known well enough to answer **whether audio or text is retained, used for model training, exposed to human review or placed in safety/abuse logs**, run the demo as local/text-only. Do not display “nothing is stored,” “zero retention” or “not used for training” unless those statements have actually been verified.

**Must do tonight — camera and feedback.** Keep camera processing entirely local. Do not write frames to disk, send frames off-device, create facial embeddings or persist tracks across sessions. Offer a touch/keyboard initiation route alongside wave detection so a person who cannot see the cue or wave can use the system independently.

Keep thumbs-up/down separate from voice content and identity. For the demonstration, the cleanest implementation is an aggregate in-memory counter discarded when the device shuts down. Do not ask party, candidate preference, intended vote or demographic profiling questions.

**Must do tonight — election information.** Prominently label the device **PROOF OF CONCEPT** and name the real operator. Do not call it “official,” use election-board seals/logos or imply government approval without written permission.

Use official election-source links and show an as-of/effective date for procedural information. Do not let the model invent polling locations, eligibility rules or filing deadlines from memory when authoritative data are unavailable.

Do not operate at an active polling location or absentee-voting site tonight. If the venue happens to be serving that function, turn off the kiosk rather than trying to reason informally about the 25/50-foot zone. RSMo §115.637's current restrictions expressly include surveying and electioneering. citeturn16view0

**Must do tonight — accessibility.** A person must be able to complete the basic demonstration without seeing a wave cue or speaking. Provide text input, captions for spoken output, visible state/error messages, large controls, sufficient contrast, back/cancel/repeat and a direct link or QR route to the official source. Title II's general effective-communication principles are useful design constraints even if tonight's operator itself is not a Title II entity. citeturn18view2

Keep a one-page internal **actual data-flow sheet** next to the device: sensor → local processing → network endpoint → vendor processing → retained artifact → deletion. This should describe the system, not contain actual visitor recordings.

## Before public deployment

**Resolve the audio question with the finished architecture.** Have Missouri counsel provide an opinion that separately addresses: private versus governmental operator; §542.402's wire/oral distinction; whether Wi-Fi/radio transport changes the oral-device analysis; cloud streaming; the local wake-word/ring buffer; active participant consent; accidental bystander speech; and what interaction constitutes adequate “prior consent.” Give counsel a packet trace/data-flow diagram, not only marketing prose. citeturn0search6turn12view0

**Complete a privacy/data inventory.** Inventory microphone samples, wake-word buffers, images, presence/wave outputs, transcripts, prompts, generated answers, network identifiers, helpfulness feedback, telemetry, crash dumps, abuse logs and backups. For each item, specify purpose, recipient, linkage across sessions, retention, deletion, disclosure/public-record status and security controls.

**Contract the cloud service deliberately.** The production agreement should answer independent model-training use, product-improvement use, human review, raw-audio retention, transcript retention, abuse logs, subprocessors, deletion SLA, backups, incident notice, encryption, tenant separation, audit rights, data location, government/public-record assistance and exit deletion. Do not let the marketing name of an API stand in for the contract.

**Map public records before promising deletion.** If any public body sponsors the kiosk, ask its records officer and counsel to classify every artifact under Chapter 610 and the applicable retention schedule. Vendor possession is not necessarily outside Sunshine Law. citeturn13view1 Determine which records may be closed under §610.021 and which may remain open. citeturn13view2

**Choose a child policy.** The simplest first-release policy is to prevent known under-13 users from using cloud voice while keeping full text/accessibility alternatives. If child voice is desired, document whether COPPA applies to the operator, whether the §312.5(c)(9) exception is being used, why each cloud provider is or is not “support for internal operations,” the deletion mechanism and the required child/privacy notices. citeturn19view0

**Create a nonpartisan content specification.** Require identical answer structure for candidates; no endorsements or recommendations; direct quotation or faithful display of official ballot language; source/effective date for procedural answers; provenance behind every election fact; abstention when no authoritative source is available; an urgent correction channel; and systematic testing for asymmetric language or factual error. For government-funded operation, explicitly test every candidate/measure mode against §115.646's advocacy prohibition. citeturn15view1

**Get the right election authority's written answer.** For a site outside Kansas City city limits but in Jackson County, start with JCEB; for a Kansas City site, use KCEB. JCEB expressly confirms that jurisdictional split. citeturn21search0turn21search3 Ask whether that authority invoked §115.637's 50-foot option for the specific election and whether a neutral kiosk or its feedback feature may be present at the proposed location.

**Avoid polling places for the first public deployment.** A library/civic-center demonstration away from active voting materially simplifies the analysis. If a future deployment is at an election site, disable feedback and do not enter the statutory zone without written approval and legal review. citeturn16view0

**Resolve campaign-finance attribution before launch.** If any campaign, political committee, ballot-measure organization, candidate, governmental body, sponsor or donor participates in content/funding, have Missouri campaign-finance counsel or the Missouri Ethics Commission determine whether Chapter 130 registration, reporting, attribution or in-kind contribution requirements apply. The operative definitions are purpose-sensitive. citeturn15view0

**Perform an accessibility audit, not merely a WCAG scan.** Evaluate physical approach/clear floor space, seated reach, keyboard/switch operation, nonvisual interaction, screen reader semantics, touch target size, captions, speech alternatives, hearing/vision/mobility/speech/cognitive use, timeout extension, error recovery and direct access to official material. For government-hosted web content, test against WCAG 2.1 AA and track the current April 26, 2027/2028 deadlines. citeturn18view0turn18view3

**Verify language obligations separately.** Obtain the current Census/DOJ §203 determination for the actual jurisdiction, identify federal funding and any Title VI language-access conditions, and ask JCEB/KCEB which translated election materials they already recognize. For ballot measures, the AI should not silently translate legally significant ballot language when an authoritative version exists.

**Build operational safety controls.** Harden the Pi, isolate credentials, use signed/controlled software, least privilege and encrypted transport, apply patches, restrict admin access, detect physical tampering, set rate limits, and provide an operator kill switch for microphone/camera. Red-team prompts seeking partisan endorsements, vote-choice collection, false deadlines, voter-suppression advice, system-prompt disclosure and fabrication of official affiliation.

## Questions for Missouri counsel and election authorities

**For Missouri recording/privacy counsel**

1. Under the final architecture, how does RSMo §542.402 treat an ordinary microphone's initial acquisition of an active user's speech by a **private** operator, given the difference between §542.402.2(2) and .2(3)? Does the answer change if the operator is acting for a county/election authority?
2. Does transmitting captured audio over Wi-Fi satisfy any of §542.402's oral-device/radio language in a way that wired Ethernet would not, and how should the initial acoustic acquisition versus later network transmission be classified?
3. Is an on-screen disclosure plus deliberate **Start voice** action sufficient “prior consent” for the active user? What records, if any, should demonstrate consent without creating unnecessary tracking data?
4. How should an unavoidable wake-word ring buffer be treated? Does memory-only local buffering constitute an interception even when never stored or transmitted?
5. How should bystander conversations be analyzed in a library, county building, election-office lobby and polling-place environment respectively?
6. What Missouri common-law privacy, constitutional, Missouri Merchandising Practices Act, tort or property theories should be added even where §§542.400-.402 do not prohibit a particular capture?
7. Has Missouri enacted, during or after the 2026 session, any comprehensive privacy/biometric provision applicable to this kiosk that is not yet obvious from the codified Revisor pages reviewed?
8. Are there Jackson County or Kansas City home-rule/municipal privacy, surveillance, camera, audio or biometric provisions that apply to the proposed installation?

**For government records/procurement counsel**

1. Which Open Oracle artifacts qualify as public records under §610.010: raw audio, transient transcript, final transcript, user prompt, model answer, feedback, safety log, source provenance, telemetry and cloud-provider logs?
2. Which may legally be discarded immediately, and which retention schedule applies?
3. Are vendor-held records “created or maintained … on behalf of” the agency within §610.010(6) under the contemplated contract? citeturn13view1
4. Which §610.021 exemptions could lawfully close particular fields, and which would remain open? citeturn13view2
5. What procurement provisions are mandatory for cloud AI: security, incident reporting, accessibility, insurance, records production, data ownership, subprocessors, deletion and audit?
6. Can the public notice promise immediate deletion, or would that conflict with an applicable retention/legal-hold requirement?

**For Missouri campaign-finance/election counsel**

1. Given the actual sponsor/funding structure, does producing and operating a candidate/ballot explainer constitute an “expenditure” under §130.011 if its purpose and implementation are neutral? citeturn15view0
2. At what point would prompt wording, curated sources or sponsor messaging make it activity intended to influence voters?
3. Are any committee registration, reporting, attribution or “paid for by” requirements applicable to this exact configuration?
4. What content-review process is sufficient for a publicly funded kiosk under §115.646? citeturn15view1
5. Does a thumbs-up/down helpfulness request constitute “surveying” under §115.637(18), regardless of whether it asks how the person voted? The statutory text creates enough risk that the feature should remain off at election sites unless counsel says otherwise. citeturn16view0
6. Can an election authority lawfully authorize an informational kiosk inside a polling building notwithstanding §115.637, or should the kiosk always remain outside the applicable statutory distance?

**For JCEB or KCEB, depending on the street address**

1. Is this address within JCEB or KCEB jurisdiction? JCEB states that Kansas City residents use KCEB while JCEB administers Jackson County outside Kansas City. citeturn21search0turn21search3
2. Has the authority posted the statutory notice extending §115.637's zone from 25 to 50 feet for the relevant election?
3. Would the authority permit a neutral informational kiosk at or near an election facility during absentee voting or election day?
4. Is a non-vote-preference helpfulness question considered prohibited “surveying” by the authority?
5. Which official source should control when state and local pages differ on registration deadlines, polling location, candidate list or ballot wording?
6. Is written permission available to use the authority's name, ballot text, URLs or logo? What wording would avoid suggesting an endorsement that has not been given?
7. Who should receive a same-day report when the kiosk discovers or produces an erroneous election answer?

**For the ADA coordinator/accessibility counsel**

1. Does the final Raspberry Pi interface qualify as “web content” under 28 CFR Part 35 Subpart H, or is it a native kiosk interface governed by Title II's general requirements without the web-specific technical standard?
2. Which provisions of the 2010 ADA Standards apply to the kiosk's mounting, accessible route, clear floor space, reach and operable parts at the chosen site?
3. What independent interaction paths are required for a person who cannot wave, see, hear, speak or accurately touch a screen?
4. Which captions, screen-reader/nonvisual controls and hearing accommodations constitute effective communication for the specific election-information service?
5. Does Section 504 apply because of HAVA or another federal funding stream?
6. What current VRA §203 and Title VI language obligations apply to the same program?

## Provisional notice and primary-source bibliography

**Provisional recording/privacy notice — subject to actual data flow, vendor terms and counsel review**

> **OPEN ORACLE — PROOF OF CONCEPT / [OPERATOR NAME]**
>
> This kiosk provides nonpartisan explanations and links to official election sources. It is **not an official election authority** unless [state the actual written authorization].
>
> **Camera:** The camera is processed on this device to detect presence and a deliberate wave. **[Only if verified: Images and video are not saved or sent off-device.]** The system does not identify people, perform facial recognition, or create face or identity profiles.
>
> **Voice:** The microphone is **off until you select “Start voice.”** While the microphone indicator is on, your speech is sent to **[vendor/service/region]** to process your request. **[Insert the actual raw-audio, transcript, safety-log, model-training and deletion practices.]** Please do not speak Social Security numbers, account credentials, medical information or other sensitive information.
>
> **Accessible alternatives:** You can use **[touch/text/keyboard/switch-access method]** without using the camera or voice. Captions are available.
>
> **Feedback:** Thumbs-up/down asks only whether an explanation was helpful. **[Explain exactly whether it is retained, aggregated or linked to the session.]** We do not ask how you intend to vote.
>
> **Election information:** Verify registration, deadlines, polling locations, ballot wording and eligibility using the linked official sources.
>
> **Voice consent:** By selecting **Start voice**, you consent to the voice capture and processing described above. **[Insert final under-13 policy.]**
>
> Privacy/contact: **[operator name, contact, privacy-policy location/QR].**

The notice should **not** say “nothing is recorded,” “nothing is stored,” “anonymous,” “never used for training” or “deleted immediately” until each statement has been tested against the Pi, browser/application, network layer, AI/speech vendor, safety logs, analytics and backups. A notice also cannot cure nonconsensual bystander capture, polling-place surveying/electioneering, inaccessible design, public-fund advocacy or inaccurate election information. citeturn12view0turn16view0turn18view2

**Primary federal sources**

- **Federal Wiretap Act/ECPA — 18 U.S.C. §2510:** definitions of oral communication and interception. citeturn12view0
- **18 U.S.C. §2511:** prohibition and party/prior-consent exceptions. citeturn12view1turn13view0
- **COPPA Rule, 16 CFR Part 312:** current child, personal-information, operator, notice, consent and security rules; the eCFR page reviewed was updated through October 7, 2026 and incorporates the April 22, 2025 amendments. citeturn19view0
- **Voting Rights Act §11(b), 52 U.S.C. §10307(b):** voter intimidation, threats and coercion. citeturn16view1
- **18 U.S.C. §594:** federal voter-intimidation offense. citeturn16view2
- **ADA Title II / DOJ:** current state/local-government accessibility framework. citeturn18view1turn18view2
- **28 CFR Part 35 Subpart H and DOJ's 2026-updated web/mobile fact sheet:** WCAG 2.1 AA and the revised 2027/2028 compliance dates. citeturn18view0turn18view3
- **Section 504:** [29 U.S.C. §794](https://www.law.cornell.edu/uscode/text/29/794).
- **Voting Rights Act §203:** [52 U.S.C. §10503](https://www.law.cornell.edu/uscode/text/52/10503).
- **Title VI:** [42 U.S.C. §2000d](https://www.law.cornell.edu/uscode/text/42/2000d).
- **HAVA voting-system requirements:** [52 U.S.C. §21081](https://www.law.cornell.edu/uscode/text/52/21081).
- **FTC Policy Statement on Biometric Information and §5:** agency enforcement policy rather than a freestanding biometric statute. citeturn4search1

**Primary Missouri sources**

- **RSMo §542.400:** interception definitions and official case annotations. citeturn0search9
- **RSMo §542.402:** Missouri interception offenses and consent exceptions. citeturn0search6
- **RSMo §407.1500:** Missouri breach-notification statute. citeturn19view1turn0search3
- **RSMo §302.170:** Department of Revenue biometric provisions. citeturn19view2
- **RSMo §610.010:** Sunshine Law definitions, including contractor-held public records. citeturn13view1
- **RSMo §610.021:** closed-record categories. citeturn13view2
- **RSMo §115.637:** election offenses, including the 2026 25/50-foot polling-place provision. citeturn15view2turn16view0
- **RSMo §115.646:** public-funds advocacy prohibition, current version effective August 28, 2026. citeturn15view1
- **RSMo §130.011:** campaign-finance definitions. citeturn15view0
- **Missouri Secretary of State Elections Division:** statewide role and decentralized local-election structure. citeturn21search16
- **Jackson County Board of Election Commissioners:** official jurisdiction statement establishing the JCEB/KCEB Kansas City split. citeturn21search0turn21search3

**Unresolved coverage that should be treated as an open issue, not as absence of law:** a complete Jackson County and Kansas City municipal-code check for audio/camera/biometric/privacy rules; the applicable Missouri/local public-record retention schedule for kiosk artifacts; current Census/DOJ VRA §203 language-coverage status for the exact jurisdiction; any late-session or not-yet-codified 2026 Missouri privacy legislation; the actual cloud-vendor/API contractual configuration; the kiosk's Title II Subpart H classification; and election-specific JCEB/KCEB notices invoking §115.637's optional 50-foot boundary.

**Bottom-line risk posture:** For tonight's adult, staffed proof of concept, the defensible architecture is **mic off until explicit opt-in; no wake phrase; no raw-content retention; local-only non-identifying camera processing; no minors on voice; no polling-place use; no vote-preference collection; visible prototype/nonofficial status; official-source citations; and a fully usable text/caption/non-camera path**. Before unattended or government deployment, the unresolved Missouri interception interpretation, government records/retention rules, vendor contract, child policy, election-authority authorization, campaign-finance/public-funds analysis, accessibility audit and language-access determination should all be closed. None of those controls, alone or together, should be treated as a legal-compliance certification. citeturn0search6turn13view1turn15view1turn16view0turn18view0turn19view0

[2026-10-11]