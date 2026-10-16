# 7 Run-Time Environments

- [7.1 Storage Organization](7.1-Storage-Organization.md)
- [7.10 References for Chapter 7](7.10-References-for-Chapter-7.md)
- [7.2 Stack Allocation of Space](7.2-Stack-Allocation-of-Space.md)
- [7.3 Access to Nonlocal Data on the Stack](7.3-Access-to-Nonlocal-Data-on-the-Stack.md)
- [7.4 Heap Management](7.4-Heap-Management.md)
- [7.5 Introduction to Garbage Collection](7.5-Introduction-to-Garbage-Collection.md)
- [7.6 Introduction to Trace-Based Collection](7.6-Introduction-to-Trace-Based-Collection.md)
- [7.7 Short-Pause Garbage Collection](7.7-Short-Pause-Garbage-Collection.md)
- [7.8 Advanced Topics in Garbage Collection](7.8-Advanced-Topics-in-Garbage-Collection.md)
- [7.9 Summary of Chapter 7](7.9-Summary-of-Chapter-7.md)

## 章首内容

Run-Time Environments
A compiler must accurately implement the abstractions embodied in the sourcelanguage definition. These abstractions typically include the concepts we discussed in Section 1.6 such as names, scopes, bindings, data types, operators, procedures, parameters, and flow-of-control constructs. The compiler must cooperate with the operating system and other systems software to support these abstractions on the target machine.
To do so, the compiler creates and manages a run-time environment in which it assumes its target programs are being executed. This environment deals with a variety of issues such as the layout and allocation of storage locations for the objects named in the source program, the mechanisms used by the target program to access variables, the linkages between procedures, the mechanisms for passing parameters, and the interfaces to the operating system, input/output devices, and other programs.
The two themes in this chapter are the allocation of storage locations and access to variables and data. We shall discuss memory management in some detail, including stack allocation, heap management, and garbage collection. In the next chapter, we present techniques for generating target code for many common language constructs.
