#!/bin/sh

# Plants
# for file in Plant_00 Plant_0 Plant_10 Plant_11 Plant_12 Plant_13 Plant_14 Plant_15 Plant_16 Plant_17 Plant_18 Plant_19 Plant_1 Plant_20 Plant_21 Plant_22 Plant_23 Plant_24 Plant_25 Plant_26 Plant_27 Plant_28 Plant_29 Plant_2 Plant_30 Plant_31 Plant_32 Plant_33 Plant_34 Plant_3 Plant_4 Plant_5 Plant_6 Plant_7 Plant_8 Plant_9
# do
# 	echo "$file"
# 	gimp --no-interface --batch '(python-fu-miasmata-merge-journal-mask RUN-NONINTERACTIVE "'${file}.png'" "research_left_mask.png" "'${file}_blank.xcf'")' --batch '(gimp-quit 1)'
# done

# # Drugs
# for file in Plant_A Plant_B Plant_C Plant_D Plant_E Plant_F Plant_H Plant_I Plant_J Plant_K Plant_X Plant_Y Plant_Z
# do
# 	echo "$file"
# 	gimp --no-interface --batch '(python-fu-miasmata-merge-journal-mask RUN-NONINTERACTIVE "'${file}.png'" "research_left_drug_mask.png" "'${file}_blank.xcf'")' --batch '(gimp-quit 1)'
# done

# Plant research
for file in RESEARCH_00 RESEARCH_0 RESEARCH_10 RESEARCH_11 RESEARCH_12 RESEARCH_13 RESEARCH_14 RESEARCH_15 RESEARCH_16 RESEARCH_17 RESEARCH_18 RESEARCH_19 RESEARCH_1 RESEARCH_20 RESEARCH_21 RESEARCH_22 RESEARCH_23 RESEARCH_24 RESEARCH_25 RESEARCH_26 RESEARCH_27 RESEARCH_28 RESEARCH_29 RESEARCH_2 RESEARCH_30 RESEARCH_31 RESEARCH_32 RESEARCH_33 RESEARCH_34 RESEARCH_3 RESEARCH_4 RESEARCH_5 RESEARCH_6 RESEARCH_7 RESEARCH_8 RESEARCH_9 Research_K
do
	echo "$file"
	gimp --no-interface --batch '(python-fu-miasmata-merge-journal-mask RUN-NONINTERACTIVE "'${file}.png'" "research_right.png" "'${file}_blank.xcf'")' --batch '(gimp-quit 1)'
done
