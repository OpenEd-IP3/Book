# Mid-term report

Now that you know how to drive your car, and hopefully have a working localization module and car model, it is time to document what you did so far in a mid-term report. This report will also form the basis of your final report.

**Report** A mid-term report explaining primarily the locallization and modeling results. Also answer the specific questions asked in the modules. 
*Suggested length:* About 15 to at most 20 pages (excluding the Appendix that lists the Python code).
The report is prepared as a group. The report is graded and contributes to your final grade.

**Preparation** Completed the preceding modules (sign-off by the TAs).

**Time duration** Two homework sessions.

## Mid-term report

The mid-term report explains your designs with its techincal details. The primary focus is to report on your results for the localization and modeling modules, but also the distnace sensor measurements should be reported. 
*Suggested length:* 15 to 20 at most 20 pages. 

Aspects on which the report is judged are:

- *Techincal content:* Theoretical justification and accuracy of the results, addressing all requested tasks. Bonus for taking the analysis/design beyond the strict scope of the related Module, in particular for introducing innovative solutions; penalty for unacceptable conceptual mistakes or unfinished work.

Proof of your results (localization algorithm, car model) using sufficiently extensive testing.

- *Quality of the submitted report:* Conformity to the requirements of a scientific report (adequate use of equations, figures, citations, cross-references), readability, layout.  
The format is of that of a technical report, and not that of a homework assignment.  Thus, the report should contain the results of the various assignments, embedded in a natural way, as these will motivate your solution. 

- *Planning and teamwork* are also to be judged. The report should also have a section that clearly describes these aspects. 

The deadline for submission is listed on Brightspace. Submit your report using the corresponding submission folder. Please use a filename that starts with your group number.

The report should be independently readable by a technically skilled committee member who is not familiar with IP3, but you can refer where needed, so don't copy large parts of this manual but summarize the scope in your own words.  Note: you cannot refer to something like `ch3' without explaining briefly what that is.

The modules suggested questions that you can answer in your report ---do this in a natural (self-contained) way.  You can also refer to additional literature that you consulted.  As mentioned, you should try to be concise, and judge yourself what is important to be included.

## How to write and structure your report

Here are some general directions on the structure and contents of your report (mid-term and final report).  For the mid-term report, the main focus will be on three sections: sensor data, localization, and car model; other chapters such as system integration and conclusions are not yet relevant and can be omitted.

Keep a clear structure and writing style. Make sure you give sufficient factual information (in particular if things don't work). The language should *not* be informal.  Keep things concise, ''bla-bla'' is not appreciated. If you make claims such as ``something is the best'', first provide evidence (or at least a motivation, or a reference to literature).

**Cover:** Make sure you specify names, study number, group number, and date.

**Introduction:** First determine who is the reader (in this case, the course coordinator, or evaluating committee member, later in life e.g., your boss). The report should be at his level: find an appropriate balance between context details and conciseness. In general, the introduction of a technical report should present the context and describe the design objectives (problems to be solved), at a sufficiently high level. 

After the problem definition/requirements and an initial analysis that identifies the critical design issues, a typical report would split the problem up into sub-problems (subsystems) which are defined in general terms in the Introduction, and developed individually in the subsequent sections. A picture (block scheme) might be helpful to show the structure and the relations among subsystems. Sometimes, after the introduction a section is needed that describes the background in more technical or mathematical detail, or analyzes the problem in more detail. For the mid-term report, that structure is probably overkill.

In general, an introduction may also contain a literature overview, references to similar work, e.g., how similar problems have been solved and what are the limitations of those solutions (thus motivating your present work), but that is probably not needed for IP3.

The sections on subsystems may follow the same structure but at a more detailed level.

Place your report in context: "This report describes ---". You don't need to motivate the project (i.e., don't include a text on the relevance of autonomous driving). ChatGPT-generated text is not appreciated.

**Sections:** You can probably skip to report on Module 1, but place the results of the other Modules each in a separate section. You don't have to repeat everything from a module, but give sufficient context to make your report independently readable. Embed the assignments in a natural way, and give them intelligible names (not "Task 1").

For each section, think of the following aspects:

- *Specifications:* What is the objective? What is given already? You may also define notation here.
- *Analysis:* What are the one or two key problems that drive the design? How can these be addressed?
- *Design:* What needs to be designed? What is your approach? Make clear what was already given and what is added by you. 
It is highly appreciated if you include an analysis that explains how accurate your system could be (or will be), in view of hardware limitations. This analysis is then backed up by the verification stage.
- *The resulting design:* This could comment on the implementation, refer to the main variables that you use, etc; generally after reading this, a reader should be able to quickly grasp the Python code in the Appendix.

- **Testing/verification:** How do you test your solution is functional and meets the specifications?  What did you measure/observe? Present your results (e.g., measurement results, a Python plot), describe what you see in each plot, and then what you can conclude from this.  Don't be naive: things don't work exactly how you design them.  Do the debugging systematically.  Be sure the plots have correct labels on the axis, and a legend on the line types if you use multiple lines in a single plot. Check the font size; the plot should be readable.

If something doesn't work, what is your hypothesis on the problem? How would you verify that hypothesis?

It is certainly not appreciated if you only say "It works" or "It didn't work" without documenting this first (i.e., show results/plots/evidence and discuss what is seen).

**For IP3, particular emphasis will be placed on the testing aspect. You cannot make claims unless you provide evidence. Your overall system will fail if a subsystem fails, and the purpose of testing is to rule out possible causes of failure.**

- *Conclusions:* Each section finished with a conclusion summarizing the results of the Module in a few lines, including claims on expected accuracy. This captures what members of the other sub-group need to know when they use your Module as a black box tool.

**System Integration:** This will be added in the final report. Apart from the integration aspects, this is a natural place to describe the GUI and its functionality. Include a screenshot.

Also in this section, you need a subsection on Verification, now on the complete design (overall test). The results of the final challenge may be added here as well. 

**Conclusions:** Clearly mention if something doesn't work. This is still the formal part of the report, so keep the language sufficiently formal until this point.

**Discussion:** Here you can include information about the (group) process and any other useful feedback. This part can also include your original planning (work division over team members and time) and the actual outcome. See the Kickoff document: how did that work out? Did everyone contribute?

The material under Discussion can be more informal. In a real (formal) report like a thesis, these sections would be omitted or worked into as an Acknowledgement or Postscript.

**Appendix:** Include Python code and/or other details on your design that may be helpful.
- Structure your code into functions. 
- Functions should have a header block that explains what the function does and what the input/output parameters are. Also include author and date information (version, history).
- Describe data structures and other global variables in sufficient detail.

Your appendix has to be sufficiently complete such that the experiments are reproducible by others.
