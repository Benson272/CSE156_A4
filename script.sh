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


# trigram categorized
python convert_infrequent.py categorize
python count_freqs.py categorized.train > categorized_gene.counts
python main.py categorized_gene.counts trigram
python eval_gene_tagger.py gene.key categorized_gene.counts.trigram