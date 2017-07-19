The goal of this research is to be able to associate topics and pins.

A topic is defined as the title of an existing Wikipedia page.

The first use case is to be able to show swimlanes for "top" and "emerging" topics
based on pin posting counts.

To achieve that, the proposal is:
* add a `source` parameter to the relevant API calls (e.g. `GET themes`)
* add a `source` field to aggregate documents in Solr (to directly support the API change)
* add a new type of document in Solr that includes a pin ID and a list of topics
 * This is a "join document" - to determine topics for a pin, one must join with
   these documents. This is because pin documents can be updated/replaced during a
   process that is not related to topic classification, and we don't want that
   action to cause the loss of topics.
 * this will allow us to create aggregations per source type (currently we're already
   getting Facebook aggregations directly from Datasift)

## Classification

At this point, the only input I'm using is the pin description, and my data set
is not labeled (meaning I do not have a corpus of pins with desired/correct related topics).
The following approaches are what I have experimented with so far:

* [TextRazor](http://textrazor.com) - a paid text analysis service
* [doc2vec](https://arxiv.org/abs/1405.4053) - a "paragraph vector" algorithm from Google
* [Solr's](http://lucene.apache.org/solr/) [More Like This](https://cwiki.apache.org/confluence/display/solr/MoreLikeThis) feature - using Solr to determine document similarity
* unigram/bigram text search
* noun phrase text search

##### Super short summary

If you'd like to reproduce these experiments, what you'll need to do is:

* [get Solr set up locally with indexed wikipedia documents](#wikipedia-in-solr)
* [run textrazor-tag.py to get baseline results from TextRazor](#pin-topic-tagging)
* run a script corresponding to the desired approach to get comparable results
* run additional scripts to see result details
* [more details here](#to-do-this-yourself)


##### [TextRazor](http://textrazor.com)

TextRazor provides a number of text analysis results, one of which is wikipedia
entity detection. With relatively short pin descriptions, this may not be the best
approach. However it does appear to do a reasonable job, and in the absence of
any labelled training data, I'm initially considering TextRazor results to be a
baseline for comparison.

##### [doc2vec](https://arxiv.org/abs/1405.4053)

First there was `word2vec`, that determined vector representations of words that
could be used in a mathematically consistent-ish way (i.e. king-man+woman=queen).
Next came `doc2vec` which attempts to do the same thing but at the document
level (i.e. construct vectors for an entire set of words).

I trained a doc2vec model on the wikipedia corpus using [gensim](https://radimrehurek.com/gensim/models/doc2vec.html),
by following along with [this tutorial](https://markroxor.github.io/gensim/static/notebooks/doc2vec-wikipedia.html).
I then tried finding wikipedia documents that are most similar to a pin description,
for example: `[model["nutella"] + model["hot"] + model["chocolate"]]`

The results I got were not entirely meaningless, but also not very useful (I got a
bunch of documents with titles that were words I didn't know - TODO paste list here).

Some additional reading indicates that short sentences may not be the best use case
for doc2vec, or perhaps there are other training options to be able to use word
vectors like I tried, or perhaps I'm just using the tool incorrectly. Further
exploration is surely in order, but this is as far as I've gotten. More details
on how to set up a machine for training and testing can be found [below](#doc2vec-on-wikipedia).

##### "[More Like This](https://cwiki.apache.org/confluence/display/solr/MoreLikeThis)" in Solr

Solr has a feature that allows one to perform a search based on an existing document
(vs. a search query). The engine uses an algorithm to determine which other documents
in the index are most similar. See http://cephas.net/blog/2008/03/30/how-morelikethis-works-in-lucene/
(or the code) for more details, but it involves normal term vectors. See https://www.reddit.com/r/MachineLearning/comments/3jr02d/how_is_word2vec_different_from_vector_space_model/
for what I think is actually a decent summary of differences between vectors as used
here compared to word2vec/doc2vec vectors.

A More Like This query can also take an entire document as the "source" document
(vs. an existing document in the index). For my investigation, I ran MLT queries
using pin descriptions as the source.

This task requires that wikipedia documents be indexed in Solr, so before you can
run the `solr-tag.py` script, you'll need a [local Solr instance set up](#wikipedia-in-solr).

##### Unigrams/bigrams

This is a brute force approach. I look at every non-stopword word and bigram
(pair of consecutive words) in the pin description, and execute a matching
text search on wikipedia page titles (for pages that are not disambiguation articles).
For example, if the pin description is "Nutella hot chocolate - the best!!",
I run searches for "nutella", "hot", "chocolate", "best", "nutella hot",
"hot chocolate" (and find 2 hits, "nutella" and "hot chocolate").

##### Noun phrases

Because the *gram approach results in quite a few topics that are not found by
TextRazor, I thought I'd try and narrow the search parameters a little bit. Instead
of looking at all unigrams/bigrams, I tried looking only at noun phrases

## Results

<table>
  <tr>
    <th>TextRazor</th>
    <th>Dandelion</th>
    <th>Solr</th>
    <th>*gram</th>
    <th>Noun Phrase</th>
    <th>IBM-NLU</th>
    <th>RAKE</th>
  </tr>
  <tr>
    <td></td>
    <td nowrap>
      matching: 2135<br/>
      textrazor only: 1411<br/>
      dandelion only: 2095<br/>
      score: 0.569076
    </td>
    <td nowrap>
      matching: 426<br/>
      textrazor only: 3300<br/>
      solr only: 2554<br/>
      score: 0.127050
    </td>
    <td nowrap>
      matching: 2402<br/>
      textrazor only: 1324<br/>
      gram only: 4217<br/>
      score: 0.464379
    </td>
    <td nowrap>
      matching: 725<br/>
      textrazor only: 3001<br/>
      noun phrase only: 1185<br/>
      score: 0.257275
    </td>
    <td nowrap>
      matching: 471<br/>
      textrazor only: 3255<br/>
      ibm-nlu only: 1042<br/>
      score: 0.179805
    </td>
    <td nowrap>
      matching: 718<br/>
      textrazor only: 3008<br/>
      rake only: 1490<br/>
      score: 0.241995
    </td>
  </tr>
  <tr>
    <td nowrap>
53: Chocolate<br/>
49: Cookie<br/>
47: Cheese<br/>
43: Do_it_yourself<br/>
43: Gluten-free_diet<br/>
39: Butter<br/>
32: Salad<br/>
30: Gluten<br/>
29: Breakfast<br/>
27: Slow_cooker<br/>
27: Cake<br/>
25: Dessert<br/>
25: Peanut<br/>
23: Sugar<br/>
23: Soup<br/>
23: Veganism<br/>
23: Bread<br/>
22: Peanut_butter<br/>
22: Pie<br/>
21: Chicken<br/>
1235 unique topics
    </td>
    <td nowrap>
123: Recipe<br/>
53: Gluten-free_diet<br/>
47: Do_it_yourself<br/>
45: Baking<br/>
39: Slow_cooker<br/>
35: Chicken<br/>
35: Physical_exercise<br/>
35: Chocolate<br/>
32: Cheese<br/>
30: Cookie<br/>
28: Chicken_as_food<br/>
28: Breakfast<br/>
27: Healthy_diet<br/>
27: Dessert<br/>
26: Veganism<br/>
26: Salad<br/>
25: Pumpkin<br/>
22: Craft<br/>
21: Child<br/>
20: Soup<br/>
1876 unique topics<br/>
    </td>
    <td nowrap>
38: List_of_America's_Test_Kitchen_episodes<br/>
30: Food_Paradise<br/>
17: Chocolate_chip_cookie<br/>
10: Everyday_Gourmet_with_Justine_Schofield<br/>
10: DIY_ethic<br/>
9: List_of_Cook's_Country_episodes<br/>
8: Breakfast<br/>
7: List_of_salads<br/>
7: Banana_bread<br/>
7: Cake<br/>
7: Gluten-free_diet<br/>
7: Chinese_chicken_salad<br/>
7: List_of_cakes<br/>
7: Smoothie<br/>
6: Carol_Kicinski<br/>
6: Macaroni_and_cheese<br/>
6: List_of_products_manufactured_by_The_Hershey_Company<br/>
6: Creative_Juice<br/>
6: Muffin<br/>
6: Chicken_soup<br/>
2341 unique topics
    </td>
    <td nowrap>
187: Recipe<br/>
84: Chicken<br/>
82: KID<br/>
72: Love<br/>
61: Chocolate<br/>
58: Idea<br/>
52: GReAT<br/>
51: Craft<br/>
49: Like<br/>
48: Day<br/>
48: Cheese<br/>
47: SiMPLE<br/>
46: Fun<br/>
43: Time<br/>
43: Cake<br/>
42: Butter<br/>
39: HomeMADE<br/>
33: Family<br/>
33: Ingredient<br/>
32: Salad<br/>
1870 unique topics
    </td>
    <td nowrap>
30: Recipe<br/>
25: Time<br/>
18: Minutes<br/>
17: Home<br/>
14: Breakfast<br/>
12: Family<br/>
12: Fun<br/>
11: Love<br/>
11: Dinner<br/>
9: Day<br/>
9: Kitchen<br/>
8: Cheese<br/>
8: God<br/>
8: Bacon<br/>
8: Life<br/>
7: Week<br/>
6: Top<br/>
6: Flavor<br/>
6: Money<br/>
6: Gluten<br/>
520 unique topics
    </td>
    <td nowrap>
8: Apple<br/>
2: YouTube<br/>
2: Starbucks<br/>
2: Anxiety<br/>
2: England<br/>
2: India<br/>
2: London<br/>
2: Milk<br/>
2: The Cheesecake Factory<br/>
2: William Shatner<br/>
2: Valentine<br/>
2: Europe<br/>
2: NBC<br/>
2: Paula Deen<br/>
1: Coit Tower<br/>
1: Ham<br/>
1: Landon<br/>
1: Paris<br/>
1: Bologna<br/>
1: 20 minutes<br/>
114 unique topics
    </td>
    <td nowrap>
42: Love<br/>
26: Recipe<br/>
26: Time<br/>
17: Home<br/>
17: Gluten<br/>
15: Family<br/>
15: Find<br/>
14: Breakfast<br/>
14: Dinner<br/>
13: Cheese<br/>
13: GReAT<br/>
10: SiMPLE<br/>
10: Kitchen<br/>
10: Year<br/>
10: Chicken<br/>
9: Summer<br/>
9: Bacon<br/>
9: Taste<br/>
9: Making<br/>
8: Creamy<br/>
767 unique topics
    </td>
  </tr>
</table>

##### Some notes about the numbers

These results were generated by examining 1500 pins (the first
1500 from a random snapshot avro file). The numbers in the second row (matching, etc)
are not the number of pins. They are the total number of topics, summed up over all
per-pin comparisons.

Concretely - I start with a list of pin descriptions (one per line). I run them
through TextRazor, and for each pin I get a list of wikipedia topics (one line per
pin, topics are comma-delimited). I do the same for each other approach, so I end up
with one results file per approach, each with the same number of lines as the number
of pins examined.

Then, for each pin, I compare the lists of topics, and see ***for that pin*** how many
match and how many are exclusively in each of TextRazor vs alternative. Then the overall
"matching" number is the sum of all matching counts for each pin. I wanted this to
represent a sense of the overlap between the various approaches.

The score number is an attempt to quantify the overlap in the range [0,1], where 0
is no overlap. The formula is:

`matching * 2 / (matching * 2 + textrazor only + approach only)`.

The numbers in the topic lists are actual topic counts. For example, of the 1500
pins, TextRazor determined that 53 of them are related to the Chocolate wikipedia article.

### Topic list comparisons

##### Dandelion
<table>
  <tr>
    <th>Matching</th>
    <th>only in TextRazor</th>
    <th>only in Dandelion</th>
  </tr>
  <tr>
    <td nowrap>
 106: Recipe<br/>
  50: Gluten-free_diet<br/>
  42: Do_it_yourself<br/>
  40: Baking<br/>
  34: Slow_cooker<br/>
  34: Chocolate<br/>
  32: Chicken<br/>
  28: Cheese<br/>
  27: Cookie<br/>
  25: Dessert<br/>
  25: Chicken_as_food<br/>
  24: Breakfast<br/>
  24: Veganism<br/>
  24: Salad<br/>
  23: Healthy_diet<br/>
  22: Physical_exercise<br/>
  20: Pumpkin<br/>
  19: Vegetable<br/>
  18: Peanut_butter<br/>
  18: Halloween<br/>
973 topics<br/>
    </td>
    <td nowrap>
only in textrazor-results.txt
  30: Gluten<br/>
  17: Kitchen_stove<br/>
  17: Italy<br/>
  11: France<br/>
   9: Bean<br/>
   8: Macaroni<br/>
   7: Protein<br/>
   7: Crock_(dishware)<br/>
   4: Salt<br/>
   4: England<br/>
   3: Wife<br/>
   3: China<br/>
   3: Curd<br/>
   3: Thailand<br/>
   3: Poland<br/>
   3: Mint_chocolate<br/>
   2: Foil_(fencing)<br/>
   2: Baking_mix<br/>
   2: Slider<br/>
   2: Blood<br/>
262 topics<br/>
    </td>
    <td nowrap>
  19: Child<br/>
  18: Flavor<br/>
  17: Italian_cuisine<br/>
  17: Craft<br/>
  16: Taste<br/>
  14: Food<br/>
  13: Handicraft<br/>
   9: Protein_(nutrient)<br/>
   8: Love<br/>
   8: Idea<br/>
   7: Confectionery<br/>
   7: Family<br/>
   7: Abdomen<br/>
   7: What's_Cookin'?<br/>
   7: Orange_(fruit)<br/>
   6: Beauty<br/>
   6: Turkey_(bird)<br/>
   5: Gift<br/>
   5: Maple_syrup<br/>
   5: Meat_tenderness<br/>
903 topics<br/>
    </td>
  </tr>
</tr></table>

##### Solr
<table>
  <tr>
    <th>Matching</th>
    <th>only in TextRazor</th>
    <th>only in Solr</th>
  </tr>
  <tr>
    <td nowrap>
  17: Chocolate_chip_cookie<br/>
   8: Breakfast<br/>
   7: Cake<br/>
   7: Gluten-free_diet<br/>
   7: Banana_bread<br/>
   7: Smoothie<br/>
   6: Muffin<br/>
   6: Macaroni_and_cheese<br/>
   6: Chicken_soup<br/>
   6: Homeschooling<br/>
   5: Do_it_yourself<br/>
   5: Cookie<br/>
   5: Dessert<br/>
   5: Chocolate_chip<br/>
   5: Casserole<br/>
   5: Veganism<br/>
   5: Peanut_butter_cookie<br/>
   5: Cheesecake<br/>
   5: Salad<br/>
   4: Pizza<br/>
348 topics
    </td>
    <td nowrap>
  53: Chocolate<br/>
  23: Sugar<br/>
  21: Chicken<br/>
  20: Christmas<br/>
  18: Ingredient<br/>
  18: Dinner<br/>
  17: Kitchen_stove<br/>
  17: Italy<br/>
  16: Vegetable<br/>
  16: Sauce<br/>
  15: Physical_exercise<br/>
  14: Tomato<br/>
  13: Paleolithic_diet<br/>
  13: Coconut<br/>
  13: Cinnamon<br/>
  13: Pumpkin<br/>
  13: Lemon<br/>
  12: Oatmeal<br/>
  12: Sandwich<br/>
  12: Lunch<br/>
887 topics
    </td>
    <td nowrap>
  38: List_of_America's_Test_Kitchen_episodes<br/>
  30: Food_Paradise<br/>
  10: Everyday_Gourmet_with_Justine_Schofield<br/>
  10: DIY_ethic<br/>
   9: List_of_Cook's_Country_episodes<br/>
   7: List_of_salads<br/>
   7: Chinese_chicken_salad<br/>
   7: List_of_cakes<br/>
   6: Carol_Kicinski<br/>
   6: List_of_products_manufactured_by_The_Hershey_Company<br/>
   6: Creative_Juice<br/>
   6: Gooey_butter_cake<br/>
   6: Printable<br/>
   5: List_of_American_desserts<br/>
   5: List_of_Bake_with_Anna_Olson_episodes<br/>
   5: Delicious_(game_series)<br/>
   5: Geography_of_Halloween<br/>
   5: List_of_pies<br/>
   5: Healthy_Lifestyles_for_High_School_Students<br/>
   5: Christmas_traditions<br/>
1993 topics
    </td>
  </tr>
</tr></table>

##### *gram

<table>
  <tr>
    <th>Matching</th>
    <th>only in TextRazor</th>
    <th>only in *gram</th>
  </tr>
  <tr>
    <td nowrap>
 187: Recipe<br/>
  84: Chicken<br/>
  61: Chocolate<br/>
  48: Cheese<br/>
  43: Cake<br/>
  42: Butter<br/>
  33: Ingredient<br/>
  32: Salad<br/>
  32: Dinner<br/>
  31: Breakfast<br/>
  30: Gluten<br/>
  30: Cream<br/>
  29: Party<br/>
  27: Soup<br/>
  26: Dessert<br/>
  25: Peanut<br/>
  23: Sugar<br/>
  23: Christmas<br/>
  23: Pie<br/>
  22: Peanut_butter<br/>
795 topics
    </td>
    <td nowrap>
  43: Do_it_yourself<br/>
  43: Gluten-free_diet<br/>
  23: Veganism<br/>
  17: Kitchen_stove<br/>
  17: Italy<br/>
  15: Physical_exercise<br/>
  13: Paleolithic_diet<br/>
  12: Pasta<br/>
  11: Icing_(food)<br/>
  11: Chicken_as_food<br/>
  10: Maize<br/>
   9: Parmigiano-Reggiano<br/>
   7: Crock_(dishware)<br/>
   7: Low-carbohydrate_diet<br/>
   6: Refrigerator<br/>
   6: Chocolate_chip_cookie<br/>
   6: Mother's_Day<br/>
   6: Egg_as_food<br/>
   6: Hors_d'oeuvre<br/>
   5: Coriander<br/>
440 topics
    </td>
    <td nowrap>
  82: KID<br/>
  72: Love<br/>
  58: Idea<br/>
  52: GReAT<br/>
  51: Craft<br/>
  49: Like<br/>
  48: Day<br/>
  47: SiMPLE<br/>
  46: Fun<br/>
  43: Time<br/>
  39: HomeMADE<br/>
  33: Family<br/>
  31: Food<br/>
  30: Home<br/>
  30: CREAM<br/>
  28: EveR<br/>
  27: Minute<br/>
  26: Creamy<br/>
  24: Take<br/>
  24: Need<br/>
1075 topics
    </td>
  </tr>
</table>

##### Noun phrase

<table>
  <tr>
    <th>Matching</th>
    <th>only in TextRazor</th>
    <th>only in Noun phrase</th>
  </tr>
  <tr>
    <td nowrap>
  30: Recipe<br/>
  14: Breakfast<br/>
  11: Dinner<br/>
   9: Kitchen<br/>
   8: Bacon<br/>
   8: Cheese<br/>
   8: God<br/>
   6: Gluten<br/>
   6: Nothing<br/>
   6: Garden<br/>
   5: Husband<br/>
   5: Lunch<br/>
   5: Butter<br/>
   5: Blog<br/>
   5: Coffee<br/>
   4: Snack<br/>
   4: Pinterest<br/>
   4: Oven<br/>
   4: Milk<br/>
   4: Sweetness<br/>
274 topics
    </td>
    <td nowrap>
  43: Do_it_yourself<br/>
  43: Gluten-free_diet<br/>
  23: Veganism<br/>
  22: Pie<br/>
  18: Ingredient<br/>
  17: Kitchen_stove<br/>
  17: Italy<br/>
  16: Potato<br/>
  16: Vegetable<br/>
  15: Physical_exercise<br/>
  14: Tomato<br/>
  14: Cheesecake<br/>
  13: Muffin<br/>
  13: Cinnamon<br/>
  13: Chocolate_chip<br/>
  13: Paleolithic_diet<br/>
  12: Pasta<br/>
  11: Blueberry<br/>
  11: Icing_(food)<br/>
  11: France<br/>
961 topics
    </td>
    <td nowrap>
  25: Time<br/>
  18: Minutes<br/>
  17: Home<br/>
  12: Family<br/>
  12: Fun<br/>
  11: Love<br/>
   9: Day<br/>
   8: Life<br/>
   7: Week<br/>
   6: Top<br/>
   6: Flavor<br/>
   6: Money<br/>
   6: Everything<br/>
   5: Child<br/>
   4: Winter<br/>
   4: Beginners<br/>
   4: World<br/>
   4: Morning<br/>
   4: Summer<br/>
   4: Anyone<br/>
246 topics
    </td>
  </tr>
</table>

##### IBM-NLU

<table>
  <tr>
    <th>Matching</th>
    <th>only in TextRazor</th>
    <th>only in IBM-NLU</th>
  </tr>
  <tr>
    <td nowrap>
    8: Apple<br/>
   2: Europe<br/>
   2: YouTube<br/>
   2: NBC<br/>
   2: Starbucks<br/>
   2: Anxiety<br/>
   2: England<br/>
   2: India<br/>
   2: London<br/>
   2: Milk<br/>
   1: Ham<br/>
   1: Paris<br/>
   1: Bologna<br/>
   1: Pisa<br/>
   1: Basil<br/>
   1: Nordstrom<br/>
   1: Michelangelo<br/>
   1: Herb<br/>
   1: Oregon<br/>
   1: Zazzle<br/>
31 topics
    </td>
    <td nowrap>
  53: Chocolate<br/>
  49: Cookie<br/>
  47: Cheese<br/>
  43: Do_it_yourself<br/>
  43: Gluten-free_diet<br/>
  39: Butter<br/>
  32: Salad<br/>
  30: Gluten<br/>
  29: Breakfast<br/>
  27: Slow_cooker<br/>
  27: Cake<br/>
  25: Dessert<br/>
  25: Peanut<br/>
  23: Sugar<br/>
  23: Soup<br/>
  23: Veganism<br/>
  23: Bread<br/>
  22: Peanut_butter<br/>
  22: Pie<br/>
  21: Chicken<br/>
1204 topics
    </td>
    <td nowrap>
   2: Paula Deen<br/>
   2: The Cheesecake Factory<br/>
   2: William Shatner<br/>
   2: Valentine<br/>
   1: Sis<br/>
   1: Camila<br/>
   1: Coit Tower<br/>
   1: Mike Colter<br/>
   1: Landon<br/>
   1: Piet Mondrian<br/>
   1: Pepa<br/>
   1: Jack Skellington<br/>
   1: 20 minutes<br/>
   1: Rev<br/>
   1: One Hour<br/>
   1: Ken Frank<br/>
   1: Greens<br/>
   1: Lois Lane<br/>
   1: Pollock<br/>
   1: Jillian Michaels<br/>
83 topics
    </td>
  </tr>
</table>

## Data files

* `pins.json.gz`: 10,000 pins in json format, extracted from a single avro snapshot file I found
* `pin-descriptions.txt`: pin descriptions extracted from the json, one per line
* `*-results.txt`: these are the outputs of the various pin/topic tagging scripts
   below. I checked in my results, but feel free to generate your own...
   
## To Do This Yourself

1. get local environment setup, you'll need:
   * avro tools: https://ahalogy.atlassian.net/wiki/display/dev/Misc
   * jq: https://stedolan.github.io/jq/download/
   * python, with an environment as specified below in the [Scripts](#scripts) section
   * [local Solr with indexed wikipedia documents](#wikipedia-in-solr)

2. get some text, in this case we're dealing with pin descriptions
   * `aws s3 ls s3://ada.a5y.com/emr/aggregation/pig/jobs/states/ | tail -3`
   * take the second to last one, call it NNNNN (see https://ahalogy.atlassian.net/wiki/spaces/inf/pages/71335947/Solr-Cloud+Operations+Run+Book#Solr-CloudOperationsRunBook-Loadingwhennobackupisavailable)
   * `aws s3 ls s3://ada.a5y.com/emr/aggregation/pig/jobs/states/NNNNN/Pins/`
   * pick a file and get it locally, any one will do
   * `aws s3 cp s3://ada.a5y.com/emr/aggregation/pig/jobs/states/NNNNN/Pins/part-r-XXXXX.avro .`
   * extract some descriptions, I'll do 500 since that's how many we can analyze per day for free with TextRazor
   * `avro tojson part-r-XXXXX.avro | head -500 | jq -r '.description.string' > descriptions.txt`
   * descriptions.txt will have one entry per line

3. get baseline results from TextRazor
   * `cat descriptions.txt | python textrazor-tag.py > tr-results.txt`
   * tr-results.txt will have a list of detected wikipedia topics, one line per description

4. get evaluation results from our own ideas, in this case I'll show the ngram results
   * write some code to try an experiment (like gram-tag.py)
   * have that code output a list of detected wikipedia topics, one line per description
   * `cat descriptions.txt | python gram-tag.py > g-results.txt`

5. compare experiment against baseline
   * `python scorer.py tr-results.txt g-results.txt`
   * `cat g-results.txt | python histogram.py`
   * `python compare.py tr-results.txt g-results.txt`

## Scripts

These scripts are all python. If you want to run them, I'd recommend setting up a
virtualenv, and then:

* `pip install -r requirements.txt`
* `python -m spacy download en`

##### pin-topic tagging

The following scripts are all run the same way:
* input: from stdin, pin descriptions, one per line
* output: to stdout, list of topics per pin, one csv list per line
* run like this: `head -1500 pin-descriptions.txt | python gram-tag.py > gram-results.txt`

The evaluation scripts are:

* `textrazor-tag.py`
 * requires a TextRazor API key (mine is hardcoded in), and note you can only make
   500 calls per day with my free tier account
* `solr-tag.py`
* `gram-tag.py`
* `noun-tag.py`
 * these three all require a local solr instance with a core called `wikipedia_core` using the `schema.xml` from this repo
 * they require solr to have the `solr.MoreLikeThisHandler` requestHandler defined in conf
 * they require a wikipedia article dump to have been [loaded into the index](#wikipedia-in-solr)

#### scorer.py

This generates the topic counts and the score in the table above. Run it like this:

`python scorer.py textrazor-results.txt gram-results.txt`

The first input is the "baseline" results to compare/score against. You can specify multiple
comparison files after the baseline.

#### histogram.py

This generates the top-n topics and shows how many pins each topic was tagged with.
You can optionally include an argument to specify n (defaults to 20). Run like this:

`cat gram-results.txt | python histogram.py`

#### compare.py

This compares exactly two results files and generates three lists: topics that exist
in both results, and topics that exist only in one or the other.

`python compare.py textrazor-results.txt gram-results.txt`

#### pin-board.py

This generates a pinterest-like/masonry layout of pins, for manual examination and/or
sanity checking. It expects one pin json document per line coming in on stdin, and
outputs to a file specified on the command line (defaults to `pin-board.html`).

`gzcat pins.json.gz | jq -c '.' | head -1500 | python pin-board.py`

Heads up - the resulting HTML takes a while to load, it's dumbly going and fetching
all images (no fancy "dynamic load as you scroll down" nonsense).

## Next steps

Further areas of exploration would include:

* Somehow use an algorithm (likely idf-based, which is quite different than idgaf)
  to help remove some of the dominant and bland topics from the gram results.
  We would need to essentially ***not*** tag some number of pins with for example
  the "recipe" topic.
* Limit the number of wikipedia pages to consider. For example we could take the 1000
  most common topics from Datasift, rather than looking at all 5+ million wikipedia articles.
* Try Solr MRT the other direction - consider a wikipedia article as the source, and
  find pins that are similar.
* Get a labeled set of pin/topic data and use that as the baseline instead
  of TextRazor - would require us humans to go through a bunch of pins and decide
  what topics we think the ideal results would be.
* Try RAKE and Maui libraries (see https://www.airpair.com/nlp/keyword-extraction-tutorial)
* Try Ranking SVM approach (see http://bdewilde.github.io/blog/2014/09/23/intro-to-automatic-keyphrase-extraction/)
* Try to construct our own machine learning/NLP algorithm/model
  * for supervised, get a labeled set of descriptions
  * define feature extraction
  * define, train, and test model
  * python: nltk, spacy, textblob, textacy, scikit-learn, tensorflow
  * java: Deeplearning4j, Stanford NLP, Apache OpenNLP, Mallet
* Find another ML/NLP service besides TextRazor
  * https://alchemy-language-demo.mybluemix.net/
  * https://cloud.google.com/natural-language/
    * [tb] Similar to TextRazor. Appears to detect more entities, pretty much one for every noun
    (unless the noun is parsed as an adjective, e.g. it doesn't get "nutella" from "nutella hot chocolate").
    Pricing would be $2,000 per month for 8 million queries. Doesn't seem to have any customization options.
  * https://aws.amazon.com/amazon-ai/
    * [tb] Entity extraction is not one of the services (AI services are around image and speech/voice). 
    They do have a ML platform, which is a layer on top of ML toolkits (like tensorflow), but this
    feels more like an option to explore if we decide to get into ML in general, with our own
    feature extraction and training/test data (assuming a supervised approach).
* Purchase TextRazor - either monthly as a service, or get it on premise
* Make use of each pin's click-through content to get much more context
* Make use of each pin's image, extracting captions to add more context

## Miscellaneous

#### Wikipedia in Solr

The `wikixml-to-solr.py` script will load articles from a wikipedia xml dump file
into a solr instance.

* install Solr locally
  * or create a solr mut:
    * follow instructions at https://ahalogy.atlassian.net/wiki/spaces/dev/pages/58785842/Development+MUTs#Development/MUTs-CustomInstancewithChefZero
    * except add `-v 128` as a `create_spot` parameter (you'll need more than the default 8GB storage)
    * and for the last chef command, instead of running the mut recipe, run these instead:
    * `sudo chef-client -z --runlist 'recipe[a5y-java-8],recipe[a5y-solr-cloud::install_solr]'`
    * ssh to the mut and `/opt/solr/bin/solr start`
* create a core, call it `wikipedia_core`
* use the `schema.xml` from this repo
* add `<requestHandler name="/mlt" class="solr.MoreLikeThisHandler"></requestHandler>` to `solrconfig.xml`
* on the machine with solr, wget a `enwiki-<date>-pages-articles.xml.bz2` file from https://dumps.wikimedia.org/enwiki/
  * this can take a couple of hours on a mut
* run `python wikixml-to-solr.py enwiki-<date>-pages-articles.xml.bz2` with the file downloaded
  * you'll probably want to run this in a `screen` since it will take many hours

#### Wikipedia in MySQL

* install MySQL locally
* create a database called `wikipedia` with username/password `ahalogy`
* follow instructions at https://dkpro.github.io/dkpro-jwpl/DataMachine/
  (this involves downloading wikipedia xml dump files, converting them to txt,
  and loading that txt into mysql)
* if you want to go from MySQL->Solr, run the java app in the `WikipediaDbToSolr` class in this repo

#### doc2vec on Wikipedia

* create an m4.2xlarge EC2 instance with 50G of disk
* `sudo apt-get install libatlas-base-dev python3-pip gfortran`
* `sudo apt-get install python3-numpy python3-scipy`
* `sudo pip3 install --upgrade gensim`
* `sudo apt-get remove python3-pip`
* `sudo apt-get install python3-setuptools`
* `easy_install3 pip`
* `sudo pip3 install ipython`
* `wget http://dumps.wikimedia.your.org/enwiki/20170301/enwiki-20170301-pages-articles.xml.bz2`
* `ipython3`
* follow along with https://markroxor.github.io/gensim/static/notebooks/doc2vec-wikipedia.html
* please note the training can take days

#### Further reading

websites of interest:
* https://www.airpair.com/nlp/keyword-extraction-tutorial
* http://bdewilde.github.io/blog/2014/09/23/intro-to-automatic-keyphrase-extraction/
* https://blog.statsbot.co/text-classifier-algorithms-in-machine-learning-acc115293278
* http://www.kdnuggets.com/2015/11/seven-steps-machine-learning-python.html
* http://www.kdnuggets.com/2017/03/seven-more-steps-machine-learning-python.html
* http://www.kdnuggets.com/2016/01/seven-steps-deep-learning.html
* http://www.nltk.org/book/ch07.html
