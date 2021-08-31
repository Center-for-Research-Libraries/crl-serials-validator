### Creating html files from markdown

This requires `pandoc` be installed, and the presence of the `pandoc.css` file. The basic commands is:

`pandoc -c pandoc.css -s --metadata pagetitle="PAPR Validator Instructions" INSTRUCTIONS.md -o Instructions.html`

`pandoc -c pandoc.css -s --metadata pagetitle="PAPR Validator Instructions" CHECKLIST_GLOSSARY.md -o Checklist_glossary.html`

`pandoc -c pandoc.css -s --metadata pagetitle="PAPR Validator Instructions" ERROR_CATEGORIES_GLOSSARY.md -o Error_categories_glossary.html`

`pandoc -c pandoc.css -s --metadata pagetitle="PAPR Validator Instructions" FOR_REVIEW_GLOSSARY.md -o For_review_glossary.html`

`pandoc -c pandoc.css -s --metadata pagetitle="PAPR Validator Instructions" ORIG_FROM_GLOSSARY.md -o Orig_from_glossary.html`

To run them all from a single command (on Linux) use:

`pandoc -c pandoc.css -s --metadata pagetitle="PAPR Validator Instructions" INSTRUCTIONS.md -o Instructions.html && pandoc -c pandoc.css -s --metadata pagetitle="PAPR Validator Instructions" CHECKLIST_GLOSSARY.md -o Checklist_glossary.html && pandoc -c pandoc.css -s --metadata pagetitle="PAPR Validator Instructions" ERROR_CATEGORIES_GLOSSARY.md -o Error_categories_glossary.html && pandoc -c pandoc.css -s --metadata pagetitle="PAPR Validator Instructions" FOR_REVIEW_GLOSSARY.md -o For_review_glossary.html && pandoc -c pandoc.css -s --metadata pagetitle="PAPR Validator Instructions" ORIG_FROM_GLOSSARY.md -o Orig_from_glossary.html`