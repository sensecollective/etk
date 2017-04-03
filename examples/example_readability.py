# This is how we intend to use it 
import sys
import os
import json
import codecs
import fnmatch
from multiprocessing import Process
from jsonpath_rw import parse
import time
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import etk


tk = etk.init()
tk.load_dictionaries()


def load_json_file(file_name):
    rules = json.load(codecs.open(file_name, 'r', 'utf-8'))
    return rules


def jl_file_iterator(file):
    with codecs.open(file, 'r', 'utf-8') as f:
        for line in f:
            document = json.loads(line)
            yield document


def jl_path_iterator(file_path):
    abs_file_path = os.path.abspath(file_path)
    if os.path.isdir(abs_file_path):
        for file in os.listdir(abs_file_path):
            if fnmatch.fnmatch(file, '*.jl'):
                yield os.path.join(abs_file_path, file)
    else:
        yield abs_file_path


def buildContent(jl, extractors):
    extractors['content_relaxed'] = tk.extract_readability(jl['raw_content'], {'recall_priority': True})
    extractors['content_strict'] = tk.extract_readability(jl['raw_content'], {'recall_priority': False})
    extractors['tables'] = tk.extract_table(jl['raw_content'])


def buildTokensAndData(jl, extractors):
    # for readability and title
    if not config['extractions']:
        raise "No extractions mentioned in config file"

    for extractions in config['extractions']:
        for path in extractions['input']:
            jsonpath_expr = parse(path)
            try:
                matches = jsonpath_expr.find(extractors)
            except Exception:
                print "No matches for ", path
                matches = []
            for match in matches:
                processDataMatch(match, extractions)


def annotateTokenToExtractions(tokens, extractions):
    for extractor, extraction in extractions.iteritems():
        input_type = extraction['input_type']
        if 'text' == input_type:
            # build text tokens
            continue

        data = extraction['result']
        for values in data:
            start = values['context']['start']
            end = values['context']['end']
            offset = 0
            for i in range(start, end):
                if 'semantic_type' not in tokens[i].keys():
                    tokens[i]['semantic_type'] = []
                temp = {}
                temp['type'] = extractor
                temp['offset'] = offset
                if offset == 0:
                    temp['length'] = end - start
                tokens[i]['semantic_type'].append(temp)
                offset += 1


def processDataMatch(match, extractions):
    if 'tokens' not in match.value.keys():
        match.value['tokens'] = tk.extract_crftokens(match.value['text'])
    if 'simple_tokens' not in match.value.keys():
        match.value['simple_tokens'] = tk.extract_tokens_from_crf(match.value['tokens'])

    data_extractors = {}
    for extractor in extractions['extractors']:
        extractor_info = extractions['extractors'][extractor]

        try:
            function_call = getattr(tk, extractor_info['extractor'])
        except Exception:
            print extractor_info['extractor'], " fucntion not found in etk"
            continue
        try:
            # intitalize the data extractor
            data_extractors[extractor] = {'input_type': 'tokens', 'extractor': extractor}

            if extractor_info['input_type'] == 'tokens' and 'name' in extractor_info['config'].keys() and 'ngrams' in extractor_info['config'].keys():
                data_extractors[extractor]['result'] = function_call(match.value['tokens'], name=extractor_info['config']['name'], ngrams=extractor_info['config']['ngrams'])
            elif extractor_info['input_type'] == 'tokens' and 'name' in extractor_info['config'].keys():
                data_extractors[extractor]['result'] = function_call(match.value['simple_tokens'], name=extractor_info['config']['name'])
            elif extractor_info['input_type'] == 'text':
                data_extractors[extractor]['result'] = function_call(match.value['text'])
            else:
                print "No matching call found for input type - ", extractor_info['input_type']
        except Exception as e:
            data_extractors[extractor]['result'] = ''
            print extractor, " crashed - ", e

    #  CLEAN THE EMPTY DATA EXTRACTORS
    data_extractors = dict((key, value) for key, value in data_extractors.iteritems() if value['result'])
    if data_extractors:
        annotateTokenToExtractions(match.value['tokens'], data_extractors)
        match.value['data_extractors'] = data_extractors


def processFile(jl):
    extractors = {}
    # Content extractors
    buildContent(jl, extractors)
    # tokens and data
    buildTokensAndData(jl, extractors)

    jl['extractors'] = extractors
    jl['raw_content'] = '...'
    o.write(json.dumps(jl) + '\n')


def write_output(out, results):
    for i in range(len(results)):
        o.write(json.dumps(results[i]) + '\n')


def write_output_record(out, result):
    o.write(json.dumps(result) + '\n')


def parallelProcess(files, outfile):
    processes = []
    for i in range(len(files)):
        p = Process(target=processFile, args=(files[i],))
        processes.append(p)
        p.start()
    for i in range(len(files)):
        processes[i].join()

if __name__ == "__main__":
    input_path = sys.argv[1]
    output_file = sys.argv[2]
    config_file = sys.argv[3]
    config = load_json_file(config_file)
    o = codecs.open(output_file, 'w', 'utf-8')
    startTime = time.time()

    if len(sys.argv) == 5:
        threads = int(sys.argv[4])
        print threads
        files, i = [], 1
        # pool = Pool(processes=threads)
        for jl in jl_file_iterator(input_path):
            files.append(jl)
            if i % (threads * threads) == 0:
                # pool.map(processFile, files)
                parallelProcess(files, o)
                files = []
            i += 1

        if files:
            # pool.map(processFile, files)
            parallelProcess(files, o)
            files = []
    else:
        for jl in jl_file_iterator(input_path):
            results = processFile(jl)
            write_output_record(o, results)
    print('The script took {0} second !'.format(time.time() - startTime))

    # for jl in jl_file_iterator(input_path):
    #     files.append(jl)
    #     if i % threads == 0:
    #         parallelProcess(files, o)
    #         files = []
    #     i += 1

    # if files:
    #     parallelProcess(files, o)
    #     files = []

    # o.close()
# if __name__ == "__main__":
#     input_path = sys.argv[1]
#     output_file = sys.argv[2]
#     config_file = sys.argv[3]
#     if len(sys.argv) == 5:
#         threads = sys.argv[4]
#     else:
#         threads = multiprocessing.cpu_count()
#     config = load_json_file(config_file)
#     o = codecs.open(output_file, 'w', 'utf-8')

#     # run in pool for extractors in batch
#     i, files = 1, []
#     print "Running with ", threads, 'threads'
#     for jl in jl_file_iterator(input_path):
#         files.append(jl)
#         if i % threads == 0:
#             parallelProcess(files, o)
#             files = []
#         i += 1

#     if files:
#         parallelProcess(files, o)
#         files = []

#     o.close()
