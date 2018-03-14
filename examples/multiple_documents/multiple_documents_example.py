import json, os, sys
from etk.etk import ETK

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

sample_input = {
    "doc_id": "123",
    "country": "Nigeria",
    "city": "Gombe",
    "date": "2015-02-28",
    "displaced": 24655,
    "type": "refugee",
    "dataset": "lakechad"
}

desired_output_parent = {
    "doc_id": "123",
    "country": "Nigeria",
    "city": "Gombe",
    "date": "2015-02-28",
    "displaced": 24655,
    "type": "refugee",
    "dataset": "lakechad",
    "victim": [
        "123/456"
    ]
}

desired_output_child = {
    "doc_id": "123/456",
    "type": ["Group"],
    "size": [24655],
    "nationality": ["Nigeria"],
    "in_event": ["123"],
    "dataset": "lakechad/victim"
}

etk = ETK()

template_based_constructor = None

doc = etk.create_document(sample_input)

# create a new empty document
new_doc = etk.create_document({})

# put some data in the new document
new_doc.store_extractions(doc.select_segments("displaced"), "size")
new_doc.store_extractions(doc.select_segments("country"), "nationality")
new_doc_dataset = doc.invoke_extractor(template_based_constructor,
                                       doc.select_segments("dataset"),
                                       template="{}/victim")
new_doc.store_extractions(new_doc_dataset, "dataset")

# set the doc_id of the new document.
# note: if using hash, must call when content is ready; greater control could be
# exercised by retrieving the JSON of the new doc, and calculating a custom doc_id.
# must do something if the user forgets to define a doc_id
new_doc.set_doc_id(new_doc.get_hash())

# in the new document, in_event points back to the parent document.
# if the doc_id of the new document is not set yet, this would error out.
new_doc.store_extractions(doc, "in_event")

# add a the new document as a value to the victim field.
# again, if the doc_id of the new document is not set yet, this would error out.
doc.store_extractions(new_doc, "victim")

# tell ETK that we want to process this new docuemtn and add it to the KG
etk.process_document(new_doc)
