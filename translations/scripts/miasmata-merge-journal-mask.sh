#!/bin/sh

# Plants
# for file in Plant_00 Plant_0 Plant_10 Plant_11 Plant_12 Plant_13 Plant_14 Plant_15 Plant_16 Plant_17 Plant_18 Plant_19 Plant_1 Plant_20 Plant_21 Plant_22 Plant_23 Plant_24 Plant_25 Plant_26 Plant_27 Plant_28 Plant_29 Plant_2 Plant_30 Plant_31 Plant_32 Plant_33 Plant_34 Plant_3 Plant_4 Plant_5 Plant_6 Plant_7 Plant_8 Plant_9
# do
# 	echo "$file"
# 	gimp --no-interface --batch '(python-fu-miasmata-merge-journal-mask RUN-NONINTERACTIVE "'${file}.png'" "research_left_mask.png" "'${file}_blank.xcf'")' --batch '(gimp-quit 1)'
# done

# Drugs
for file in Plant_A Plant_B Plant_C Plant_D Plant_E Plant_F Plant_H Plant_I Plant_J Plant_K Plant_X Plant_Y Plant_Z
do
	echo "$file"
	gimp --no-interface --batch '(python-fu-miasmata-merge-journal-mask RUN-NONINTERACTIVE "'${file}.png'" "research_left_drug_mask.png" "'${file}_blank.xcf'")' --batch '(gimp-quit 1)'
done
