class Edge
{
public:
    int a;
    int b;
    int w;

    Edge():a(0), b(0), w(0){}

    Edge(int a, int b, int w)
    {
        this->a = a;
        this->b = b;
        this->w = w;
    }

    bool operator<(const Edge &other)
    {
        if (this->w > other.w)
        {
            return true;
        }
        return false;
    }
};