#!/usr/bin/env bash

# #baseline converted
# python convert_infrequent.py
# python count_freqs.py converted.train > converted_gene.counts
# python main.py converted_gene.counts baseline
# python eval_gene_tagger.py gene.key converted_gene.counts.baseline

# #baseline categorized
# python convert_infrequent.py categorize
# python count_freqs.py categorized.train > categorized_gene.counts
# python main.py categorized_gene.counts baseline
# python eval_gene_tagger.py gene.key categorized_gene.counts.baseline

# #trigram converted
# python convert_infrequent.py
# python count_freqs.py converted.train > converted_gene.counts
# python main.py converted_gene.counts trigram
# python eval_gene_tagger.py gene.key converted_gene.counts.trigram


# # trigram categorized
python convert_infrequent.py categorize
python count_freqs.py categorized.train > categorized_gene.counts
python main.py categorized_gene.counts trigram
python eval_gene_tagger.py gene.key categorized_gene.counts.trigram

#4gram converted
python convert_infrequent.py
python count_freqs.py converted.train > four_gram_gene.counts
python main.py four_gram_gene.counts 4
python eval_gene_tagger.py gene.key four_gram_gene.counts.four_gram

#4gram categorized
python convert_infrequent.py categorize
python count_freqs.py categorized.train > four_gram_categorized_gene.counts
python main.py four_gram_categorized_gene.counts 4
python eval_gene_tagger.py gene.key four_gram_categorized_gene.counts.four_gram