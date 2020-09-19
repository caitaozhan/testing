#include <iostream>
#include <vector>
#include <array>
#include <string>
#include <random>
#include <algorithm>
#include <unordered_set>
#include <unordered_map>
#include <experimental/algorithm>
#include <iterator>
#include <chrono>
#include "Edge.h"
using namespace std;
using namespace chrono;


/*
    /usr/bin/g++ -O3 -g0 /home/caitao/Project/testing/maximum-weight-matching/greedy3.cpp -o /home/caitao/Project/testing/maximum-weight-matching/greedy3
*/


void timeit(system_clock::time_point start, const string & str)
{
    auto end = system_clock::now();
    auto duration = duration_cast<microseconds>(end - start);
    cout<<str<<double(duration.count()) * microseconds::period::num / microseconds::period::den<<endl;
}

/* this is modern C++ code using C++11 and above standards. However, the syntax is a little bit verbose */
int main()
{
    int N = 1000;
    int MAX_WEIGHT = 10000;
    random_device rd;
    mt19937 gen(rd());
    uniform_int_distribution<> distrib(100, 10000);     // random number generator
    vector<int> right;
    for (int i = 0; i < N; i++)
    {
        right.push_back(i+N);   // nodes on the left hand side are from 0 to N-1, the nodes on the right hand side are from N to 2N-1
    }
    vector<Edge> edges;  // vector is essentially a dynamic array from the standard library. I always prefer using a vector in C++. There might be a better option. Edge is a class encapsulating an edge
    for (int i = 0; i < N; i++)
    {
        vector<int> samples;
        experimental::sample(right.begin(), right.end(), std::back_inserter(samples), int(N/10), gen);  // sampling n/10 numbers from n numbers
        for (int j: samples)
        {
            int cost = distrib(gen);
            Edge edge(i, j, cost);
            edges.push_back(edge);
        }
    }

    auto start0 = system_clock::now();
    Edge buckets[MAX_WEIGHT+1][20];         // C-style array
    int  index[MAX_WEIGHT+1] = {0};         // track the size of each bucket in use
    timeit(start0, "Initial time  = ");

    auto start = system_clock::now();
    for (int i = 0; i < edges.size(); i++)
    {
        buckets[edges[i].w][index[edges[i].w]] = edges[i];
        index[edges[i].w] += 1;
    }
    timeit(start, "sorting time  = ");

    start = system_clock::now();
    int visited[2*N] = {false};                // the binary array
    int weight_sum = 0;
    for (int w = MAX_WEIGHT; w >= 100; w--)
    {
        for (int i = 0; i < index[w]; i++)
        {
            Edge &edge = buckets[w][i];
            if (visited[edge.a] == false && visited[edge.b] == false)
            {
                weight_sum += edge.w;
                visited[edge.a] = true;
                visited[edge.b] = true;
            }
        }
    }
    timeit(start,  "matching time = ");
    timeit(start0, "total time    = ");
    cout<<"weight = "<<weight_sum<<endl;
}