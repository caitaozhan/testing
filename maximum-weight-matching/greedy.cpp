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


int main()
{
    int N = 1000;
    random_device rd;
    mt19937 gen(rd());
    uniform_int_distribution<> distrib(100, 10000);
    vector<int> right;
    for (int i = 0; i < N; i++)
    {
        right.push_back(i+N);
    }
    vector<Edge> edges;
    for (int i = 0; i < N; i++)
    {
        vector<int> samples;
        experimental::sample(right.begin(), right.end(), std::back_inserter(samples), int(N/10), gen);
        for (int j: samples)
        {
            int cost = distrib(gen);
            Edge edge(i, j, cost);
            edges.push_back(edge);
        }
    }
    cout<<"size:"<<edges.size()<<endl;

    auto start = system_clock::now();
    sort(edges.begin(), edges.end());
    auto end = system_clock::now();
    auto duration = duration_cast<microseconds>(end - start);
    cout<<"sorting time = "<<double(duration.count()) * microseconds::period::num / microseconds::period::den<<endl;
    unordered_set<int> left_set, right_set;
    unordered_map<int, int> match;
    int weight_sum = 0;
    for (int i = 0; i < edges.size(); i++)
    {
        if (left_set.find(edges[i].a) == left_set.end() && right_set.find(edges[i].b) == right_set.end())
        {
            weight_sum += edges[i].w;
            left_set.insert(edges[i].a);
            right_set.insert(edges[i].b);
            match[edges[i].a] = edges[i].b;
        }
    }
    end = system_clock::now();
    duration = duration_cast<microseconds>(end - start);
    cout<<"total time = "<<double(duration.count()) * microseconds::period::num / microseconds::period::den<<endl;
    cout<<"weight = "<<weight_sum<<";  "<<match.size()<<endl;
}