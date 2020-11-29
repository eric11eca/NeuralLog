
## Linguistic Categorization

The dataset is designed to allow for analyzing many levels of natural language understanding, from word meaning and sentence structure to high-level reasoning and application of world knowledge. To make this kind of analysis feasible, we first identify four broad categories of phenomena:

-   Lexical Semantics
-   Predicate-Argument Structure
-   Logic
-   Knowledge and Common Sense

However, since these are vague and often arguable when it comes to entailment, we divide each into a larger set of fine-grained subcategories. Every example in the dataset is labeled with at least one fine-grained category, and many examples have more than one, often spanning multiple coarse-grained categories as well, since they often inevitably cooccur, especially when using natural sentences. Having a large set of fine-grained categories allows us to ensure a baseline level of diversity of phenomena in the diagnostic dataset, while also providing a powerful error analysis tool to GLUE users.

Descriptions of all of the fine-grained categories are given below. Bear in mind that these are just one lens that can be used to understand linguistic phenomena and entailment, and since our understanding of how language works is incomplete, there is room to argue about how examples should be categorized, what the categories should be, and, for some fine-grained subcategories, which coarse-grained category they should be placed under. These categories are not based on any particular linguistic theory, but broadly based on issues that linguists have often identified and modeled in the study of syntax and semantics. When doing error analysis according to any of these categories, please first read their description and look at some examples.

### Lexical Semantics

These phenomena center on aspects of  _word meaning_.

#### Lexical Entailment

Entailment can be applied not only on the sentence level, but the word level. For example, we say  `dog`  lexically entails  `animal`  because anything that is a dog is also an animal, and  `dog`  lexically contradicts  `cat`  because it's impossible to be both at once. This applies to all kinds of words (nouns, adjectives, verbs, many prepositions, etc.) and the relationship between lexical and sentential entailment has been deeply explored, e.g., in  [systems](https://nlp.stanford.edu/~wcmac/papers/natlog-wtep07.pdf)  of  [Natural](https://nlp.stanford.edu/~wcmac/papers/natlog-iwcs09.pdf)  [Logic](https://web.stanford.edu/~icard/logic&language/CSLIworkshop.pdf). This connection often hinges on  [_monotonicity_](https://gluebenchmark.com/diagnostics#monotonicity)  in language, so many Lexical Entailment examples will also be tagged with one of the Monotone categories, though we don't do this in every case (see  [Definite Descriptions and Monotonicity](https://gluebenchmark.com/diagnostics#definitedescriptionsandmonotonicity)).

#### Morphological Negation

This is a special case of lexical contradiction where one word is derived from the other: from  `affordable`  to  `unaffordable`,  `agree`  to  `disagree`, etc. We also include examples like  `ever`  and  `never`. We also label these examples with  [Negation](https://gluebenchmark.com/diagnostics#negation)  or  [Double Negation](https://gluebenchmark.com/diagnostics#doublenegation), since they can be viewed as involving a word-level logical negation.

#### Factivity

Propositions appearing in a sentence may be in any entailment relation with the sentence as a whole, depending on the context in which they appear. In many cases, this is determined by lexical triggers (usually verbs or adverbs) in the sentence. For example,

-   `I recognize that X`  entails  `X`
-   `I did not recognize that X`  entails  `X`
-   `I believe that X`  does not entail  `X`
-   `I am refusing to do X`  contradicts  `I am doing X`
-   `I am not refusing to do X`  does not contradict  `I am doing X`
-   `I almost finished X`  contradicts  `I finished X`
-   `I barely finished X`  entails  `I finished X`

Constructions like the one with  `recognize`  are often called  _factive_, since the entailment (of  `X`  above, regarded as a presupposition) persists even under negation. Constructions like the one with  `refusing`  above are often called  _implicative_, and are sensitive to negation. There are also cases where a sentence (non-)entails the existence of an entity mentioned in it, e.g.,

-   `I have found a unicorn`  entails  `A unicorn exists`
-   `I am looking for a unicorn`  doesn't necessarily entail  `A unicorn exists`

Readings where the entity does not necessarily exist are often called  _intensional readings_, since they seem to deal with the properties denoted by a description (its  _intension_) rather than being reducible to the set of entities that match the description (its  _extension_, which in cases of non-existence will be empty).

We place all examples involving these phenomena under the label of Factivity. While it often depends on context to determine whether a nested proposition or existence of an entity is entailed by the overall statement, very often it relies heavily on lexical triggers, so we place the category under Lexical Semantics.

#### Symmetry/Collectivity

Some propositions denote symmetric relations, while others do not; e.g.,

-   `John married Gary`  entails  `Gary married John`
-   `John likes Gary`  does not entail  `Gary likes John`

For symmetric relations, they can often be rephrased by collecting both arguments into the subject:

-   `John met Gary`  entails  `John and Gary met`

Whether a relation is symmetric, or admits collecting its arguments into the subject, is often determined by its head word (e.g.,  `like`,  `marry`  or  `meet`), so we classify it under Lexical Semantics.

#### Redundancy

If a word can be removed from a sentence without changing its meaning, that means the word's meaning was more-or-less adequately expressed by the sentence; so, identify these cases reflects an understanding of both lexical and sentential semantics.

#### Named Entities

Words often name entities that exist out in the world. There are many different kinds of understanding we might wish to understand about these names, including their compositional structure (for example,  `the Baltimore Police`  is the same as  `the Police of the City of Baltimore`) or their real-world referents and acronym expansions (for example,  `SNL`  is  `Saturday Night Live`). This category is closely related to  [World Knowledge](https://gluebenchmark.com/diagnostics#worldknowledge), but focuses on the semantics of names as lexical items rather than background knowledge about their denoted entities.

#### Quantifiers

Logical quantification in natural language is often expressed through lexical triggers such as  `every`,  `most`,  `some`, and  `no`. While we reserve the categories in  [Quantification](https://gluebenchmark.com/diagnostics#quantification)  and  [Monotonicity](https://gluebenchmark.com/diagnostics#monotonicity)  for entailments involving operations on these quantifiers and their arguments, we choose to regard the interchangeability of quantifiers (e.g., in many cases  `most`  entails  `many`) as a question of lexical semantics.

### Predicate-Argument Structure

An important component of understanding the meaning of a sentence is understanding how its parts are composed together into a whole. In this category, we address issues across that spectrum, from syntactic ambiguity to semantic roles and coreference.

#### Syntactic Ambiguity: Relative Clauses, Coordination Scope

These two categories deal purely with resolving syntactic ambiguity. Relative clauses and coordination scope are both sources of a great amount of ambiguity in English.

#### Prepositional phrases

Prepositional phrase attachment is a particularly difficult problem that syntactic parsers in NLP systems continue to struggle with. We view it as a problem both of syntax and semantics, since prepositional phrases can express a wide variety of semantic roles and often semantically apply beyond their direct syntactic attachment.

#### Core Arguments

Verbs select for particular arguments, especially as their subject and object, which might be interchangeable depending on the context or the surface form. One example is the  _ergative alternation_:

-   `Jake broke the vase`  entails  `the vase broke`.
-   `Jake broke the vase`  does not entail  `Jake broke`.

Other rearrangements of core arguments, such as those seen in  [Symmetry/Collectivity](https://gluebenchmark.com/diagnostics#symmetrycollectivity), also fall under the Core Arguments label.

#### Alternations: Active/Passive, Genitives/Partitives, Nominalization, Datives

All four of these categories correspond to  _syntactic alternations_  that are known to follow specific patterns in English:

-   Active/Passive:  `I saw him`  is equivalent to  `He was seen by me`  and entails  `He was seen`.
-   Genitives/Partitives:  `the elephant's foot`  is the same thing as  `the foot of the elephant`.
-   Nominalization:  `I caused him to submit his resignation`  entails  `I caused the submission of his resignation`.
-   Datives:  `I baked him a cake`  entails  `I baked a cake for him`  and  `I baked a cake`  but not  `I baked him`.

#### Ellipsis/Implicits

Often, the argument of a verb or other predicate is omitted (_elided_) in the text, with the reader filling in the gap. We can construct entailment examples by explicitly filling in the gap with the correct or incorrect referents.

For example:

-   Premise:  `Putin is so entrenched within Russia’s ruling system that many of its members can imagine no other leader.`
-   Entails:  `Putin is so entrenched within Russia’s ruling system that many of its members can imagine no other leader than Putin.`
-   Contradicts:  `Putin is so entrenched within Russia’s ruling system that many of its members can imagine no other leader than themselves.`

This is often regarded as a special case of  _anaphora_, but we decided to split out these cases from explicit anaphora, which is often also regarded as a case of coreference (and attempted to some degree in modern coreference resolution systems).

#### Anaphora/Coreference

_Coreference_  refers to when multiple expressions refer to the same entity or event. It is closely related to  _Anaphora_, where the meaning of an expression depends on another (antecedent) expression in context. These phenomena have significant overlap, for example, with pronouns (`she`,  `we`,  `it`), which are anaphors that are co-referent with their antecedents. However, they also may occur independently, for example, coreference between two definite noun phrases (e.g.,  `Theresa May`  and  `the British Prime Minister`) that refer to the same entity, or anaphora from a word like  `other`  which requires an antecedent to distinguish something from. In this category we only include cases where there is an explicit phrase (anaphoric or not) that is co-referent with an antecedent or other phrase.

We construct examples for these in much the same way as for  [Ellipsis/Implicits](https://gluebenchmark.com/diagnostics#ellipsisimplicits).

#### Intersectivity

Many modifiers, especially adjectives, allow  _non-intersective_  uses, which affect their entailment behavior. For example:

-   Intersective:  `He is a violinist and an old surgeon`  entails  `He is an old violinist`  and  `He is a surgeon`
-   Non-intersective:  `He is a violinist and a skilled surgeon`  does  _not_  entail  `He is a skilled violinist`
-   Non-intersective:  `He is a fake surgeon`  does  _not_  entail  `He is a surgeon`

Generally, an  _intersective_  use of a modifier, like  `old`  in  `old men`, is one which may be interpreted as referring to the set of entities with both properties (they are  `old`  and they are  `men`). Linguists often formalize this using set intersection, hence the name.

It is related to  [Factivity](https://gluebenchmark.com/diagnostics#factivity); for example  `fake`  may be regarded as a counter-implicative modifier, and these examples will be labeled as such. However, we choose to categorize intersectivity under predicate-argument structure rather than lexical semantics, because generally the same word will admit both intersective and non-intersective uses, so it may be regarded as an ambiguity of argument structure.

#### Restrictivity

`Restrictivity`  is most often used to refer to a property of uses of noun modifiers; in particular, a  _restrictive_  use of a modifier is one that serves to identify the entity or entities being described, whereas a  _non-restrictive_  use adds extra details to the identified entity. The distinction can often be highlighted by entailments:

-   Restrictive:  `I finished all of my homework due today`  does not entail  `I finished all of my homework`
-   Non-restrictive:  `I got rid of all those pesky bedbugs`  entails  `I got rid of all those bedbugs`.

Modifiers that are commonly used non-restrictively are appositives, relative clauses starting with  `which`  or  `who`  (although these  _can_  be restrictive, despite what your English teacher might tell you), and expletives (e.g.  `pesky`). However, non-restrictive uses can appear in many forms.

Ambiguity in restrictivity is often employed in certain kinds of  [jokes](https://xkcd.com/90/)  (warning: language).

### Logic

Once you understand the structure of a sentence, there is often a baseline set of shallow conclusions you can draw using logical operators.

There is a long tradition of modeling natural language semantics using the mathematical tools of logic. Indeed, the development of mathematical logic was initially by questions about natural language meaning, from Aristotelian syllogisms to Fregean symbols. The notion of entailment is also borrowed from mathematical logic. So it is no surprise that logic plays an important role in natural language inference.

#### Propositional Structure: Negation, Double Negation, Conjunction, Disjunction, Conditionals

All of the basic operations of propositional logic appear in natural language, and we tag them where they are relevant to our examples:

-   Negation:  `The cat sat on the mat`  contradicts  `The cat did not sit on the mat`.
-   Double negation:  `The market is not impossible to navigate`  entails  `The market is possible to navigate`.
-   Conjunction:  `Temperature and snow consistency must be just right`  entails  `Temperature must be just right`.
-   Disjunction:  `Life is either a daring adventure or nothing at all`  does not entail, but is entailed by,  `Life is a daring adventure`.
-   Conditionals:  `If both apply, they are essentially impossible`  does not entail  `They are essentially impossible`.

Conditionals are a little bit more complicated because their use in language does not always mirror their meaning in logic. For example, they may be used at a higher level than the at-issue assertion:

-   `If you think about it, it's the perfect reverse psychology tactic`  entails  `It's the perfect reverse psychology tactic`

#### Quantification: Universal, Existential

Quantifiers are often triggered by words such as  `all`,  `some`,  `many`, and  `no`. There is a rich body of work modeling their meaning in mathematical logic with generalized quantifiers. In these two categories, we focus on straightforward inferences from the natural language analogs of universal and existential quantification:

-   Universal:  `All parakeets have two wings`  entails, but is not entailed by  `My parakeet has two wings`.
-   Existential:  `Some parakeets have two wings`  does not entail, but is entailed by  `My parakeet has two wings`.

#### Monotonicity: Upward Monotone, Downward Monotone, Non-Monotone

Monotonicity is a property of argument positions in certain logical systems. In general, it gives a way of deriving entailment relations between expressions that differ on only one subexpression. In language, it can explain how some entailments propagate through logical operators and quantifiers.

For example, note that  `pet`  entails  `pet squirrel`, which further entails  `happy pet squirrel`. We can demonstrate how the quantifiers  `a`,  `no`  and  `exactly one`  differ with respect to monotonicity:

-   `I have a pet squirrel`  entails  `I have a pet`, but not  `I have a happy pet squirrel`.
-   `I have no pet squirrels`  does not entail  `I have no pets`, but does entail  `I have no happy pet squirrels`.
-   `I have exactly one pet squirrel`  entails neither  `I have exactly one pet`  nor  `I have exactly one happy pet squirrel`.

In all of these examples, the pet squirrel appears in what we call the  _restrictor_  position of the quantifier. We say:

-   `a`  is  _upward monotone_  in its restrictor: an entailment in the restrictor yields an entailment of the whole statement.
-   `no`  is  _downward monotone_  in its restrictor: an entailment in the restrictor yields an entailment of the whole statement  _in the opposite direction_.
-   `exactly one`  is  _non-monotone_  in its restrictor: entailments in the restrictor do not yield entailments of the whole statement.

In this way, entailments between sentences that are built off of entailments of sub-phrases almost always rely on monotonicity judgments; see, for example,  [Lexical Entailment](https://gluebenchmark.com/diagnostics#lexicalentailment). However, because this is such a general class of sentence pairs, to keep the Logic category meaningful we do not always tag these examples with monotonicity; see  [Definite Descriptions and Monotonicity](https://gluebenchmark.com/diagnostics#definitedescriptionsandmonotonicity)  for details.

To draw an analogy, these types of monotonicity are closely related to  [covariance, contravariance, and invariance](https://en.wikipedia.org/wiki/Covariance_and_contravariance_(computer_science))  of type arguments in programming languages with subtyping.

#### Richer Logical Structure: Intervals/Numbers, Temporal

There are some higher-level facets of reasoning that have been traditionally modeled using logic; these include actual mathematical reasoning (entailments based off of numbers) and temporal reasoning (which is often modeled as reasoning about a mathematical timeline).

-   Intervals/Numbers:  `I have had more than 2 drinks tonight`  entails  `I have had more than 1 drink tonight`.
-   Temporal:  `Mary left before John entered`  entails  `John entered after Mary left`.

### Knowledge & Common Sense

Strictly speaking, world knowledge and common sense are required on every level of language understanding, for disambiguating word senses, syntactic structures, anaphora, and more. So our entire suite (and any test of entailment) does test these features to some degree. However, in these categories, we gather examples where the entailment rests not only on correct disambiguation of the sentences, but also application of extra knowledge, whether it is concrete knowledge about world affairs or more common-sense knowledge about word meanings or social or physical dynamics.

#### World Knowledge

In this category we focus on knowledge that can clearly be expressed as facts, as well as broader and less common geographical, legal, political, technical, or cultural knowledge. Examples:

-   `This is the most oniony article I've seen on the entire internet`  entails  `This article reads like satire`.
-   `The reaction was strongly exothermic`  entails  `The reaction media got very hot`.
-   `There are amazing hikes around Mt. Fuji`  entails  `There are amazing hikes in Japan`  but not  `There are amazing hikes in Nepal`.

#### Common Sense

In this category we focus on knowledge that is more difficult to express as facts and that we expect to be possessed by most people independent of cultural or educational background. This includes a basic understanding of physical and social dynamics as well as lexical meaning (beyond simple lexical entailment or logical relations). Examples:

-   `The announcement of Tillerson’s departure sent shock waves across the globe`  contradicts  `People across the globe were prepared for Tillerson's departure`.
-   `Marc Sims has been seeing his barber once a week, for several years`  entails  `Marc Sims has been getting his hair cut once a week, for several years.`
-   `Hummingbirds are really attracted to bright orange and red (hence why the feeders are usually these colours)`  entails  `The feeders are usually coloured so as to attract hummingbirds`.
