#include <iostream>
#include <vector>
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

    auto start = system_clock::now();
    vector<vector<Edge>> buckets(MAX_WEIGHT + 1, vector<Edge>());
    for (int i = 0; i < edges.size(); i++)
    {
        buckets[edges[i].w].emplace_back(edges[i]);  // putting the edge into the correct bucket according to the weight
    }
    auto end = system_clock::now();
    auto duration = duration_cast<microseconds>(end - start);
    cout<<"sorting time = "<<double(duration.count()) * microseconds::period::num / microseconds::period::den<<endl;
    
    vector<bool> visited(2*N, false);                // the binary array
    unordered_map<int, int> match;
    int weight_sum = 0;
    for (int i = MAX_WEIGHT; i >= 100; i--)
    {
        for (const Edge &edge: buckets[i])
        {
            if (visited[edge.a] == false && visited[edge.b] == false)
            {
                weight_sum += edge.w;
                visited[edge.a] = true;
                visited[edge.b] = true;
                match[edge.a] = edge.b;
            }
        }
        // if (match.size() == 900)
        // {
        //     break;
        // }
    }

    end = system_clock::now();
    duration = duration_cast<microseconds>(end - start);
    cout<<"total time = "<<double(duration.count()) * microseconds::period::num / microseconds::period::den<<endl;
    cout<<"weight = "<<weight_sum<<";  number of edges in the match = "<<match.size()<<endl;
}