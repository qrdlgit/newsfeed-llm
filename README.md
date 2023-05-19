# newsfeed-llm
newsfeeds powered filtered by llms such as GPT4

The goal of this project is to have the code entirely written by GPT4.  Note that 'expert-in-the-loop' will be a part of it. AutoGPT4 type code generation, afaict, doesn't work.   Maybe AutoGPT5!

Here is the process I followed.  

Requirements doc:

1. create a requirement doc, more detailed the better.  keep it simple
2. Paste in spec, ask “What are all the questions I need to answer to get a detailed requirement specification for the above?”
3. Paste in spec + GPT4 provided prompts + answers + ”Please create detailed requirement specifications"
4. Review all artifacts provided so far, if not completely satisfied, clarify details in spec to better guide GPT4 and loop back to 1

I feel that is a very successful proces and what it has produced is actually quite good for my purposes.  The “What are all the questions I need to answer to get a detailed requirement specification for the above?” is a powerful prompt addition.

I am working on the design doc right now.  It will probably have a similar iterative process to the requirements doc.  It's a bit trickier than the requirements doc because design is a much harder problem than features.  Right now, I'm using a tool similar to https://github.com/qrdlgit/simbiotico  but is more textual based.  I'll release a video soon, but it's somewhat similar to this: https://www.youtube.com/watch?v=MIfhunAwZew  (true story:  I just found this video today, and yes, it's pretty much what I've built.  Zeitgeist and serendipity are a thing.

For the code, I've tried this in the past with mixed success:

1. create specification, more technical the better.
2. Paste in spec, ask “What are the prompts I need to ask GPT4 to get all the code for the component above?”
3. Paste in spec + GPT4 provided prompts + “Please list all the files, with brief summaries and public apis you will generate using these prompts that you provided for the above specified component”
4. Paste in spec + prompts + GPT4 provided files / public apis + “Please provide a high level description of the sequences and execution flow for component as described by the specification, prompts that you provided, and the files / public apis that you provided.”
5. Review all artifacts provided so far, if not completely satisfied, clarify details in spec to better guide GPT4 and loop back to 1


