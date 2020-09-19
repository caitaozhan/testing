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
    int MAX_WEIGHT = 10000;
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
    vector<vector<Edge>> buckets(MAX_WEIGHT + 1, vector<Edge>());
    for (int i = 0; i < edges.size(); i++)
    {
        buckets[edges[i].w].emplace_back(edges[i]);
    }
    auto end = system_clock::now();
    auto duration = duration_cast<microseconds>(end - start);
    cout<<"sorting time 2 = "<<double(duration.count()) * microseconds::period::num / microseconds::period::den<<endl;
    vector<bool> visited(2*N, false);
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
    }
    end = system_clock::now();
    duration = duration_cast<microseconds>(end - start);
    cout<<"total time = "<<double(duration.count()) * microseconds::period::num / microseconds::period::den<<endl;
    cout<<"weight = "<<weight_sum<<";  "<<match.size()<<endl;
}