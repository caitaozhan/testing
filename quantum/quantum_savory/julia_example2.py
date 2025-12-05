import numpy as np
from juliacall import Main as jl


def example1():
    jl.seval("""
    module MyModule
        export MyPoint, scale_point, sum_array

        # A simple immutable struct
        struct MyPoint
            x::Float64
            y::Float64
        end

        # Scale a point by a factor
        scale_point(p::MyPoint, factor::Float64) = MyPoint(p.x * factor, p.y * factor)

        # Sum an array of numbers
        sum_array(a::AbstractVector{<:Real}) = sum(a)
    end
    """)
    mymodule = jl.MyModule

    py_arr = np.array([1,2,3,4])
    print("Python array:", py_arr, type(py_arr))

    total = mymodule.sum_array(py_arr)
    print("sum from julia:", total, type(total))


def example2():
    jl.seval("""
             module Foo
                export hello
                hello() = println("Hi from Julia")
             end
             """)
    foo = jl.Foo
    print(foo.hello)


def example3():
    jl.seval("using QuantumSavory")
    # jl.seval("using LinearAlgebra")


def example4():
    from juliacall import Main as jl
    print(jl.seval("VERSION"))

if __name__ == "__main__":
    example1()
    example2()
    example3()
    example4()
