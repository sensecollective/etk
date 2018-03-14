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
doc.store(doc.select("displaced"), "size")
doc.store(doc.select("country"), "nationality")
dataset = doc.apply(template_based_constructor, doc.select("dataset"), template="{}/victim")
new_doc.store(dataset, "dataset")

# set the doc_id of the new document.
# note: if using hash, must call when content is ready; greater control could be
# exercised by retrieving the JSON of the new doc, and calculating a custom doc_id.
# must do something if the user forgets to define a doc_id
new_doc.doc_id = etk.hash(new_doc.value)


print(json.dumps(new_doc, indent=2))

# in the new document, in_event points back to the parent document.
new_doc.store(doc.select("doc_id"), "in_event")

# add a the new document as a value to the victim field.
doc.store(new_doc.select("doc_id"), "victim")

# tell ETK that we want to process this new docuemtn and add it to the KG
etk.process_document(new_doc)
